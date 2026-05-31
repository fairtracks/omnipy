from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable

_DEFAULT_MAX_PROBE_ITEMS = 1024
_DEFAULT_STRING_CHUNK_SIZE = 256
_DEFAULT_WIDTH_STABILIZATION_WINDOW = 2

_probe_render_active_ctx_var: ContextVar[bool] = ContextVar(
    '_probe_render_active_ctx_var',
    default=False,
)


@dataclass(frozen=True)
class _PanelPreviewBudget:
    width_budget: int | None
    height_budget: int | None


@dataclass
class _PreviewPruningMemo:
    probe_cache: dict[tuple[int, int, int, int, int], tuple[int, int]] = field(default_factory=dict)
    panel_cache: dict[tuple[int, _PanelPreviewBudget, int, int, int, int, int],
                      int | None] = field(default_factory=dict)
    active_object_ids: set[int] = field(default_factory=set)


@dataclass(frozen=True)
class _ChunkPlan:
    total_chunks: int
    prefix_builder: Callable[[int], object]


def _maybe_prune_draft_panel(
    draft_panel: Any,
    *,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo | None = None,
    max_probe_items: int = _DEFAULT_MAX_PROBE_ITEMS,
    width_stabilization_window: int = _DEFAULT_WIDTH_STABILIZATION_WINDOW,
) -> Any:
    if _is_probe_render_active():
        return draft_panel

    prunable_content = _content_for_pruning(draft_panel)

    budget = _derive_budget(draft_panel)
    plan = _build_prunable_chunk_plan(prunable_content, budget)
    if plan is None:
        return draft_panel

    if memo is None:
        memo = _PreviewPruningMemo()

    panel_key = _panel_cache_key(
        draft_panel=draft_panel,
        budget=budget,
        max_probe_items=max_probe_items,
        width_stabilization_window=width_stabilization_window,
    )
    cached_panel = _cached_panel_if_any(draft_panel, memo, panel_key, plan)
    if cached_panel is not None:
        return cached_panel

    prefix_size = _compute_prefix_size_fail_open(
        draft_panel=draft_panel,
        prunable_content=prunable_content,
        budget=budget,
        plan=plan,
        probe_render=probe_render,
        memo=memo,
        max_probe_items=max_probe_items,
        width_stabilization_window=width_stabilization_window,
    )

    memo.panel_cache[panel_key] = prefix_size
    if prefix_size is None or prefix_size >= plan.total_chunks:
        return draft_panel

    return _panel_with_prefix(draft_panel, plan, prefix_size)


def _derive_budget(draft_panel: Any) -> _PanelPreviewBudget:
    inner_frame = getattr(draft_panel, 'inner_frame', draft_panel.frame)
    dims = inner_frame.dims
    return _PanelPreviewBudget(width_budget=dims.width, height_budget=dims.height)


def _content_for_pruning(draft_panel: Any) -> object:
    if _content_is_non_debug_model_with_supported_inner_content(draft_panel):
        return draft_panel.content.content

    return draft_panel.content


def _content_is_non_debug_model_with_supported_inner_content(draft_panel: Any) -> bool:
    if getattr(draft_panel.config, 'debug', False):
        return False

    try:
        from omnipy.data.model import is_model_instance
    except Exception:
        return False

    content = draft_panel.content
    if not is_model_instance(content):
        return False

    return _is_supported_content(getattr(content, 'content', None))


def _is_probe_render_active() -> bool:
    return _probe_render_active_ctx_var.get()


@contextmanager
def _set_probe_render_active() -> Any:
    token = _probe_render_active_ctx_var.set(True)
    try:
        yield
    finally:
        _probe_render_active_ctx_var.reset(token)


def _is_supported_content(content: object) -> bool:
    return isinstance(content, (str, bytes, bytearray, dict, list, tuple))


def _build_prunable_chunk_plan(
    content: object,
    budget: _PanelPreviewBudget,
) -> _ChunkPlan | None:
    if budget.width_budget is None and budget.height_budget is None:
        return None

    if not _is_supported_content(content):
        return None

    if _requires_bounded_width(content) and budget.width_budget is None:
        return None

    plan = _build_chunk_plan(content)
    if plan.total_chunks <= 1:
        return None

    return plan


def _requires_bounded_width(content: object) -> bool:
    return not isinstance(content, (str, bytes, bytearray))


def _cached_panel_if_any(
    draft_panel: Any,
    memo: _PreviewPruningMemo,
    panel_key: tuple[int, _PanelPreviewBudget, int, int, int, int, int],
    plan: _ChunkPlan,
) -> Any | None:
    if panel_key not in memo.panel_cache:
        return None

    cached_prefix_size = memo.panel_cache[panel_key]
    if cached_prefix_size is None or cached_prefix_size >= plan.total_chunks:
        return draft_panel

    return _panel_with_prefix(draft_panel, plan, cached_prefix_size)


def _compute_prefix_size_fail_open(
    *,
    draft_panel: Any,
    prunable_content: object,
    budget: _PanelPreviewBudget,
    plan: _ChunkPlan,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    max_probe_items: int,
    width_stabilization_window: int,
) -> int | None:
    object_id = id(prunable_content)
    if object_id in memo.active_object_ids:
        return None

    memo.active_object_ids.add(object_id)
    try:
        return _find_prefix_size(
            draft_panel=draft_panel,
            budget=budget,
            plan=plan,
            probe_render=probe_render,
            memo=memo,
            max_probe_items=max_probe_items,
            width_stabilization_window=width_stabilization_window,
        )
    except Exception:
        return None
    finally:
        memo.active_object_ids.discard(object_id)


def _build_chunk_plan(content: object) -> _ChunkPlan:
    if isinstance(content, str):
        chunks = _chunk_str(content)
        return _ChunkPlan(total_chunks=len(chunks), prefix_builder=lambda n: ''.join(chunks[:n]))

    if isinstance(content, (bytes, bytearray)):
        bytes_content = bytes(content)
        chunks = _chunk_bytes(bytes_content)
        return _ChunkPlan(
            total_chunks=len(chunks),
            prefix_builder=lambda n: _restore_bytes_type(content, b''.join(chunks[:n])),
        )

    if isinstance(content, dict):
        items = list(content.items())
        return _ChunkPlan(
            total_chunks=len(items),
            prefix_builder=lambda n: type(content)(items[:n]),
        )

    if isinstance(content, list):
        return _ChunkPlan(total_chunks=len(content), prefix_builder=lambda n: content[:n])

    if isinstance(content, tuple):
        return _ChunkPlan(total_chunks=len(content), prefix_builder=lambda n: content[:n])

    raise TypeError(f'Unsupported content type: {type(content)!r}')


def _chunk_str(text: str) -> list[str]:
    if '\n' in text:
        return text.splitlines(keepends=True)

    return [
        text[start:start + _DEFAULT_STRING_CHUNK_SIZE]
        for start in range(0, len(text), _DEFAULT_STRING_CHUNK_SIZE)
    ]


def _chunk_bytes(content: bytes) -> list[bytes]:
    if b'\n' in content:
        return content.splitlines(keepends=True)

    return [
        content[start:start + _DEFAULT_STRING_CHUNK_SIZE]
        for start in range(0, len(content), _DEFAULT_STRING_CHUNK_SIZE)
    ]


def _restore_bytes_type(original: object, value: bytes) -> bytes | bytearray:
    if isinstance(original, bytearray):
        return bytearray(value)
    return value


def _panel_with_prefix(draft_panel: Any, plan: _ChunkPlan, prefix_size: int) -> Any:
    prefix_content = plan.prefix_builder(prefix_size)

    if _content_is_non_debug_model_with_supported_inner_content(draft_panel):
        model_copy = draft_panel.content.copy(deep=False)
        model_copy.content = prefix_content
        return draft_panel.create_modified_copy(content=model_copy)

    return draft_panel.create_modified_copy(content=prefix_content)


def _find_prefix_size(
    *,
    draft_panel: Any,
    budget: _PanelPreviewBudget,
    plan: _ChunkPlan,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    max_probe_items: int,
    width_stabilization_window: int,
) -> int | None:
    cap = min(max_probe_items, plan.total_chunks)
    if cap <= 0:
        return None

    growth_history: list[tuple[int, int, int]] = []
    prev_n = 0
    n = 1
    stop_reason: str | None = None

    while True:
        rendered_width, rendered_height = _probe_prefix(
            draft_panel=draft_panel,
            plan=plan,
            prefix_size=n,
            probe_render=probe_render,
            memo=memo,
        )
        growth_history.append((n, rendered_width, rendered_height))

        height_reached = (
            budget.height_budget is not None and rendered_height > budget.height_budget)
        width_stable = _width_stabilized(
            width_history=[width for _, width, _ in growth_history],
            width_stabilization_window=width_stabilization_window,
        )
        width_stable_allowed = (
            budget.height_budget is None or rendered_height >= budget.height_budget)
        reached_end = n >= plan.total_chunks
        reached_cap = n >= cap

        if height_reached:
            stop_reason = 'height'
            break

        if width_stable and width_stable_allowed:
            stop_reason = 'width'
            break

        if reached_end:
            stop_reason = 'end'
            break

        if reached_cap:
            stop_reason = 'cap'
            break

        prev_n = n
        n = min(n * 2, cap, plan.total_chunks)

    if stop_reason in ('end', 'cap'):
        return None

    assert stop_reason in ('height', 'width')
    low = max(1, prev_n)
    high = n

    while low < high:
        mid = (low + high) // 2
        if _prefix_satisfies_stop_condition(
                draft_panel=draft_panel,
                budget=budget,
                plan=plan,
                prefix_size=mid,
                max_prefix_size=cap,
                stop_reason=stop_reason,
                probe_render=probe_render,
                memo=memo,
                width_stabilization_window=width_stabilization_window):
            high = mid
        else:
            low = mid + 1

    return low


def _prefix_satisfies_stop_condition(
    *,
    draft_panel: Any,
    budget: _PanelPreviewBudget,
    plan: _ChunkPlan,
    prefix_size: int,
    max_prefix_size: int,
    stop_reason: str,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    width_stabilization_window: int,
) -> bool:
    if stop_reason == 'height':
        if budget.height_budget is None:
            return False
        _, rendered_height = _probe_prefix(
            draft_panel=draft_panel,
            plan=plan,
            prefix_size=prefix_size,
            probe_render=probe_render,
            memo=memo,
        )
        return rendered_height > budget.height_budget

    width_history: list[int] = []

    if budget.height_budget is not None:
        _, rendered_height = _probe_prefix(
            draft_panel=draft_panel,
            plan=plan,
            prefix_size=prefix_size,
            probe_render=probe_render,
            memo=memo,
        )
        if rendered_height < budget.height_budget:
            return False

    for offset in range(width_stabilization_window + 1):
        probe_size = min(prefix_size + offset, max_prefix_size, plan.total_chunks)
        rendered_width, _ = _probe_prefix(
            draft_panel=draft_panel,
            plan=plan,
            prefix_size=probe_size,
            probe_render=probe_render,
            memo=memo,
        )
        width_history.append(rendered_width)

    return _width_stabilized(width_history, width_stabilization_window)


def _probe_prefix(
    *,
    draft_panel: Any,
    plan: _ChunkPlan,
    prefix_size: int,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
) -> tuple[int, int]:
    cache_key = _probe_cache_key(draft_panel, prefix_size)
    cached = memo.probe_cache.get(cache_key)
    if cached is not None:
        return cached

    prefix_panel = _panel_with_prefix(draft_panel, plan, prefix_size)
    rendered_width, rendered_height = probe_render(prefix_panel)

    result = (int(rendered_width), int(rendered_height))
    memo.probe_cache[cache_key] = result
    return result


def _width_stabilized(width_history: list[int], width_stabilization_window: int) -> bool:
    if width_stabilization_window <= 0:
        return True

    required_samples = width_stabilization_window + 1
    if len(width_history) < required_samples:
        return False

    tail = width_history[-required_samples:]
    return len(set(tail)) == 1


def _probe_cache_key(draft_panel: Any, prefix_size: int) -> tuple[int, int, int, int, int]:
    frame_hash = hash(draft_panel.frame)
    config_hash = hash(draft_panel.config)
    printer_hash = hash(getattr(draft_panel.config, 'printer', None))
    return (id(draft_panel.content), prefix_size, frame_hash, config_hash, printer_hash)


def _panel_cache_key(
    *,
    draft_panel: Any,
    budget: _PanelPreviewBudget,
    max_probe_items: int,
    width_stabilization_window: int,
) -> tuple[int, _PanelPreviewBudget, int, int, int, int, int]:
    config_hash = hash(draft_panel.config)
    printer_hash = hash(getattr(draft_panel.config, 'printer', None))
    return (
        id(draft_panel.content),
        budget,
        hash(draft_panel.frame),
        config_hash,
        printer_hash,
        max_probe_items,
        width_stabilization_window,
    )


__all__ = ['_PreviewPruningMemo', '_maybe_prune_draft_panel']
