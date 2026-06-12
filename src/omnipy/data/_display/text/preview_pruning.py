from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from itertools import islice
from math import ceil
from typing import Any, Callable

_DEFAULT_STRING_CHUNK_SIZE = 256
_DEFAULT_WIDTH_STABILIZATION_WINDOW = 2
_DEFAULT_COARSENESS_ALPHA = 0.4
_DEFAULT_MAX_DESCENT_DEPTH = 5
_DEFAULT_MAX_PROMOTIONS = 3

_probe_render_active_ctx_var: ContextVar[bool] = ContextVar(
    '_probe_render_active_ctx_var',
    default=False,
)


def _log_prune(msg: str) -> None:
    from omnipy.shared.constants import VERBOSE_PRUNE

    if VERBOSE_PRUNE:
        print(f'[PRUNE] {msg}')


@dataclass(frozen=True)
class _PanelPreviewBudget:
    width_budget: int | None
    height_budget: int | None


@dataclass
class _PreviewPruningMemo:
    probe_cache: dict[tuple[int, int, int, int, int, int], tuple[int,
                                                                 int]] = field(default_factory=dict)
    active_object_ids: set[int] = field(default_factory=set)


@dataclass(frozen=True)
class _ChunkPlan:
    total_chunks: int
    prefix_builder: Callable[[int], object]
    cache_discriminator: int


@dataclass(frozen=True)
class _ChildLocator:
    kind: str  # sequence | mapping
    index: int
    key: object | None = None


@dataclass(frozen=True)
class _ChunkPath:
    content: object
    parent: _ChunkPath | None = None
    parent_locator: _ChildLocator | None = None
    depth: int = 0


def _maybe_prune_draft_panel(
    draft_panel: Any,
    *,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo | None = None,
    width_stabilization_window: int = _DEFAULT_WIDTH_STABILIZATION_WINDOW,
) -> Any:
    if _is_probe_render_active():
        _log_prune('Skipping pruning: probe render is already active')
        return draft_panel

    prunable_content = _content_for_pruning(draft_panel)
    budget = _derive_budget(draft_panel)

    if _build_prunable_chunk_plan(prunable_content, budget) is None:
        _log_prune(f'Skipping pruning: {_pruning_skip_reason(prunable_content, budget)}')
        return draft_panel

    if memo is None:
        memo = _PreviewPruningMemo()

    selected_path = _select_active_chunk_path(
        root_content=prunable_content,
        budget=budget,
        width_stabilization_window=width_stabilization_window,
    )
    if selected_path is None:
        _log_prune('Skipping pruning: unable to select deterministic chunk path safely')
        return draft_panel

    pruned_content = _compute_pruned_content_with_promotions(
        draft_panel=draft_panel,
        selected_path=selected_path,
        budget=budget,
        probe_render=probe_render,
        memo=memo,
        width_stabilization_window=width_stabilization_window,
    )
    if pruned_content is None:
        _log_prune('Skipping pruning: no reduction found')
        return draft_panel

    return draft_panel.create_modified_copy(content=pruned_content)


def _derive_budget(draft_panel: Any) -> _PanelPreviewBudget:
    inner_frame = getattr(draft_panel, 'inner_frame', draft_panel.frame)
    dims = inner_frame.dims
    return _PanelPreviewBudget(width_budget=dims.width, height_budget=dims.height)


def _content_for_pruning(draft_panel: Any) -> object:
    return draft_panel.content


def _is_probe_render_active() -> bool:
    return _probe_render_active_ctx_var.get()


@contextmanager
def _set_probe_render_active() -> Any:
    token = _probe_render_active_ctx_var.set(True)
    try:
        yield
    finally:
        _probe_render_active_ctx_var.reset(token)


def _is_sliceable(content: object) -> bool:
    try:
        content[:0]  # type: ignore[operator]
        return True
    except (TypeError, KeyError):
        return False


def _build_prunable_chunk_plan(content: object, budget: _PanelPreviewBudget) -> _ChunkPlan | None:
    if budget.width_budget is None and budget.height_budget is None:
        return None
    if budget.height_budget is None:
        return None

    if _looks_like_mapping(content) and not _has_deterministic_mapping_order(content):
        return None

    if not _is_sliceable(content) and not _looks_like_mapping(content):
        return None

    plan = _build_chunk_plan(content)
    if plan is None:
        return None

    return plan


def _pruning_skip_reason(content: object, budget: _PanelPreviewBudget) -> str:
    if budget.width_budget is None and budget.height_budget is None:
        return 'unbounded width and height budget'
    if budget.height_budget is None:
        return 'full view (unbounded height budget)'

    if _looks_like_mapping(content) and not _has_deterministic_mapping_order(content):
        return f'unsupported mapping ordering for {type(content)!r}'

    if not _is_sliceable(content) and not _looks_like_mapping(content):
        return f'unsupported (not sliceable) content type {type(content)!r}'

    plan = _build_chunk_plan(content)
    if plan is None:
        return 'unsupported content type for chunking'
    if plan.total_chunks <= 1:
        return 'content already within one chunk'

    return 'unknown reason'


def _effective_coarseness_threshold(
    *,
    height_budget: int | None,
    width_stabilization_window: int,
    alpha: float = _DEFAULT_COARSENESS_ALPHA,
) -> int:
    """Compute the adaptive chunk-count threshold used for descent.

    Args:
        height_budget: Available panel height for rendered content.
        width_stabilization_window: Probe window used by prefix sizing.
        alpha: Scaling factor for the base threshold.

    Returns:
        Effective minimum chunk threshold for selecting the active path.
    """
    if height_budget is None:
        t_base = 16
    else:
        t_base = max(2 * height_budget, height_budget + width_stabilization_window + 1)

    return max(4, ceil(alpha * t_base))


def _select_active_chunk_path(
    *,
    root_content: object,
    budget: _PanelPreviewBudget,
    width_stabilization_window: int,
    max_descent_depth: int = _DEFAULT_MAX_DESCENT_DEPTH,
) -> _ChunkPath | None:
    """Select a single deterministic path for hierarchical pruning.

    Args:
        root_content: Top-level content considered for preview pruning.
        budget: Width/height budgets for the preview panel.
        width_stabilization_window: Probe width-stability window.
        max_descent_depth: Maximum number of child descents to attempt.

    Returns:
        The chosen chunk path, or ``None`` when fail-open conditions apply.
    """
    if _looks_like_mapping(root_content) and not _has_deterministic_mapping_order(root_content):
        return None

    threshold = _effective_coarseness_threshold(
        height_budget=budget.height_budget,
        width_stabilization_window=width_stabilization_window,
    )

    current_path = _ChunkPath(content=root_content)

    for _ in range(max_descent_depth + 1):
        count = _cheap_chunk_count(current_path.content)
        if count is None:
            return None

        if count >= threshold:
            return current_path

        child_path, must_fail_open = _first_eligible_child_path(current_path)
        if must_fail_open:
            return None
        if child_path is None:
            return current_path

        current_path = child_path

    return current_path


def _cheap_chunk_count(content: object) -> int | None:
    """Return a cheap chunk count or ``None`` when unsafe/unavailable.

    Args:
        content: Candidate content object.

    Returns:
        Cheaply computed chunk count if available, else ``None``.
    """
    if isinstance(content, (str, bytes, bytearray, list, tuple, dict)):
        return len(content)

    if _looks_like_mapping(content):
        try:
            return len(content)  # type: ignore[arg-type]
        except TypeError:
            return None

    try:
        total = len(content)  # type: ignore[arg-type]
    except TypeError:
        return None

    if _is_sliceable(content):
        return total

    return None


def _is_descendable_container(content: object) -> bool:
    """Check whether a child content object is safe to descend into.

    Args:
        content: Candidate child content.

    Returns:
        ``True`` if hierarchical descent is allowed for this content.
    """
    if isinstance(content, (str, bytes, bytearray)):
        return False

    if isinstance(content, (list, tuple, dict)):
        return True

    if _looks_like_mapping(content):
        return _has_deterministic_mapping_order(content)

    return _is_sliceable(content)


def _first_eligible_child_path(path: _ChunkPath) -> tuple[_ChunkPath | None, bool]:
    """Locate the first descendable child path.

    Args:
        path: Current chunk path.

    Returns:
        Tuple of ``(child_path, must_fail_open)`` where ``must_fail_open`` is
        ``True`` when child metadata cannot be established safely.
    """
    content = path.content

    if isinstance(content, (list, tuple)):
        for idx, child in enumerate(content):
            if not _is_descendable_container(child):
                continue

            child_count = _cheap_chunk_count(child)
            if child_count is None:
                return None, True

            return (
                _ChunkPath(
                    content=child,
                    parent=path,
                    parent_locator=_ChildLocator(kind='sequence', index=idx),
                    depth=path.depth + 1,
                ),
                False,
            )

        return None, False

    if isinstance(content, dict):
        for idx, key in enumerate(content):
            child = content[key]
            if not _is_descendable_container(child):
                continue

            child_count = _cheap_chunk_count(child)
            if child_count is None:
                return None, True

            return (
                _ChunkPath(
                    content=child,
                    parent=path,
                    parent_locator=_ChildLocator(kind='mapping', index=idx, key=key),
                    depth=path.depth + 1,
                ),
                False,
            )

        return None, False

    return None, False


def _compute_pruned_content_with_promotions(
    *,
    draft_panel: Any,
    selected_path: _ChunkPath,
    budget: _PanelPreviewBudget,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    width_stabilization_window: int,
    max_promotions: int = _DEFAULT_MAX_PROMOTIONS,
) -> object | None:
    """Compute pruned content from selected path with bounded promotions.

    Args:
        draft_panel: Panel being pruned.
        selected_path: Initially selected active chunk path.
        budget: Preview budget constraints.
        probe_render: Render probe callback used during prefix search.
        memo: Shared probe/pruning memoization.
        width_stabilization_window: Probe width-stability window.
        max_promotions: Maximum upward promotions if path underfills.

    Returns:
        Root-level pruned content, or ``None`` when pruning should fail open.
    """
    promotions = 0
    current_path = selected_path

    while True:
        prune_result, should_promote = _attempt_path_prune(
            draft_panel=draft_panel,
            path=current_path,
            budget=budget,
            probe_render=probe_render,
            memo=memo,
            width_stabilization_window=width_stabilization_window,
        )
        if prune_result is not None:
            return prune_result
        if not should_promote:
            return None

        if current_path.parent is None or promotions >= max_promotions:
            return None

        promotions += 1
        current_path = current_path.parent


def _attempt_path_prune(
    *,
    draft_panel: Any,
    path: _ChunkPath,
    budget: _PanelPreviewBudget,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    width_stabilization_window: int,
) -> tuple[object | None, bool]:
    """Attempt pruning at one path and report whether to promote parent.

    Args:
        draft_panel: Panel being pruned.
        path: Active chunk path currently evaluated.
        budget: Preview budget constraints.
        probe_render: Render probe callback used during prefix search.
        memo: Shared probe/pruning memoization.
        width_stabilization_window: Probe width-stability window.

    Returns:
        Tuple ``(pruned_content, should_promote_parent)``.
    """
    plan = _build_chunk_plan(path.content)
    if plan is None:
        return None, False

    prefix_size, had_probe_error = _compute_prefix_size_fail_open(
        draft_panel=draft_panel,
        prunable_content=path.content,
        budget=budget,
        plan=plan,
        probe_render=probe_render,
        memo=memo,
        width_stabilization_window=width_stabilization_window,
    )
    if had_probe_error:
        return None, False

    if prefix_size is not None and prefix_size < plan.total_chunks:
        if not _should_apply_prefix_reduction(
                content=path.content, total_chunks=plan.total_chunks, prefix_size=prefix_size):
            return None, False

        pruned_content = _build_root_prefix_content_for_path(
            path=path,
            path_plan=plan,
            prefix_size=prefix_size,
        )
        if pruned_content is None:
            return None, False

        _log_prune(f'Pruned: {plan.total_chunks} -> {prefix_size} items')
        return pruned_content, False

    try:
        underfills_viewport = _path_underfills_viewport(
            draft_panel=draft_panel,
            budget=budget,
            plan=plan,
            probe_render=probe_render,
            memo=memo,
        )
    except Exception:
        _log_prune('Skipping pruning: probe error while checking underfill')
        return None, False

    return None, underfills_viewport


def _should_apply_prefix_reduction(*, content: object, total_chunks: int, prefix_size: int) -> bool:
    """Decide whether a computed prefix reduction is meaningful enough.

    Args:
        content: Content object being reduced.
        total_chunks: Total chunk count in the current chunk plan.
        prefix_size: Candidate retained prefix size.

    Returns:
        ``True`` when the reduction should be applied.
    """
    if _looks_like_mapping(content):
        return (total_chunks - prefix_size) >= 2

    return True


def _compute_prefix_size_fail_open(
    *,
    draft_panel: Any,
    prunable_content: object,
    budget: _PanelPreviewBudget,
    plan: _ChunkPlan,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    width_stabilization_window: int,
) -> tuple[int | None, bool]:
    """Find prefix size while guarding recursion and probe failures.

    Args:
        draft_panel: Panel being probed.
        prunable_content: Content object whose prefix is being measured.
        budget: Preview budget constraints.
        plan: Chunk plan for prefix construction.
        probe_render: Render probe callback used during prefix search.
        memo: Shared probe/pruning memoization.
        width_stabilization_window: Probe width-stability window.

    Returns:
        Tuple ``(prefix_size, had_probe_error)``.
    """
    object_id = id(prunable_content)
    if object_id in memo.active_object_ids:
        _log_prune('Skipping pruning: detected active recursion for content object')
        return None, True

    memo.active_object_ids.add(object_id)
    try:
        return (
            _find_prefix_size(
                draft_panel=draft_panel,
                budget=budget,
                plan=plan,
                probe_render=probe_render,
                memo=memo,
                width_stabilization_window=width_stabilization_window,
            ),
            False,
        )
    except Exception:
        _log_prune('Skipping pruning: probe error while computing prefix size')
        return None, True
    finally:
        memo.active_object_ids.discard(object_id)


def _path_underfills_viewport(
    *,
    draft_panel: Any,
    budget: _PanelPreviewBudget,
    plan: _ChunkPlan,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
) -> bool:
    """Check whether a full path render still underfills height budget.

    Args:
        draft_panel: Panel being probed.
        budget: Preview budget constraints.
        plan: Chunk plan for the currently selected path.
        probe_render: Render probe callback used during prefix probing.
        memo: Shared probe/pruning memoization.

    Returns:
        ``True`` when rendered height is below the height budget.
    """
    if budget.height_budget is None:
        return False

    _, rendered_height = _probe_prefix(
        draft_panel=draft_panel,
        plan=plan,
        prefix_size=plan.total_chunks,
        probe_render=probe_render,
        memo=memo,
    )
    return rendered_height < budget.height_budget


def _build_root_prefix_content_for_path(
    *,
    path: _ChunkPath,
    path_plan: _ChunkPlan,
    prefix_size: int,
) -> object | None:
    """Rebuild root content from a pruned child path prefix.

    Args:
        path: Active chunk path where prefix reduction happened.
        path_plan: Chunk plan for the terminal path content.
        prefix_size: Number of chunks to keep at terminal path.

    Returns:
        Root-level content with prefix embedded along the selected path,
        or ``None`` if reconstruction fails.
    """
    prefix_content = path_plan.prefix_builder(prefix_size)
    current_path = path

    while current_path.parent is not None:
        parent_locator = current_path.parent_locator
        if parent_locator is None:
            return None

        prefix_content = _embed_child_prefix_into_parent(
            parent_content=current_path.parent.content,
            parent_locator=parent_locator,
            child_prefix_content=prefix_content,
        )
        if prefix_content is None:
            return None

        current_path = current_path.parent

    return prefix_content


def _embed_child_prefix_into_parent(
    *,
    parent_content: object,
    parent_locator: _ChildLocator,
    child_prefix_content: object,
) -> object | None:
    """Embed a pruned child prefix into its parent prefix content.

    Args:
        parent_content: Original parent container.
        parent_locator: Locator describing the child position in parent.
        child_prefix_content: Pruned child content to splice into parent.

    Returns:
        Parent prefix content with updated child, or ``None`` on mismatch.
    """
    if parent_locator.kind == 'sequence':
        if not isinstance(parent_content, (list, tuple)):
            return None

        parent_prefix = list(parent_content[:parent_locator.index + 1])
        if not parent_prefix:
            return None

        parent_prefix[-1] = child_prefix_content
        if isinstance(parent_content, tuple):
            return tuple(parent_prefix)
        return parent_prefix

    if parent_locator.kind == 'mapping':
        if not isinstance(parent_content, dict) or parent_locator.key is None:
            return None

        prefix_mapping: dict[object, object] = {}
        for idx, key in enumerate(parent_content):
            if idx > parent_locator.index:
                break
            if key == parent_locator.key:
                prefix_mapping[key] = child_prefix_content
            else:
                prefix_mapping[key] = parent_content[key]

        return type(parent_content)(prefix_mapping)

    return None


def _build_chunk_plan(content: object) -> _ChunkPlan | None:
    """Build the first applicable chunking plan for content.

    Args:
        content: Content object to chunk.

    Returns:
        Chunk plan when content is chunkable, otherwise ``None``.
    """
    return (_build_builtin_chunk_plan(content) or _build_sequence_like_chunk_plan(content)
            or _build_mapping_like_chunk_plan(content))


def _build_builtin_chunk_plan(content: object) -> _ChunkPlan | None:
    """Build chunk plan for built-in str/bytes/dict content.

    Args:
        content: Candidate content object.

    Returns:
        Chunk plan for supported built-ins, else ``None``.
    """
    if isinstance(content, str):
        chunks = _chunk_str(content)
        return _ChunkPlan(
            total_chunks=len(chunks),
            prefix_builder=lambda n: ''.join(chunks[:n]),
            cache_discriminator=id(content),
        )

    if isinstance(content, (bytes, bytearray)):
        bytes_content = bytes(content)
        chunks = _chunk_bytes(bytes_content)
        return _ChunkPlan(
            total_chunks=len(chunks),
            prefix_builder=lambda n: _restore_bytes_type(content, b''.join(chunks[:n])),
            cache_discriminator=id(content),
        )

    if isinstance(content, dict):
        total = len(content)
        if total <= 0:
            return None
        return _ChunkPlan(
            total_chunks=total,
            prefix_builder=lambda n: type(content)
            (islice(content.items(), n)),  # type: ignore[call-arg]
            cache_discriminator=id(content),
        )

    return None


def _build_sequence_like_chunk_plan(content: object) -> _ChunkPlan | None:
    """Build chunk plan for sequence-like objects via slicing.

    Args:
        content: Candidate sequence-like content.

    Returns:
        Chunk plan when ``len`` and slicing are supported, else ``None``.
    """
    try:
        total = len(content)  # type: ignore[arg-type]
        content[:0]  # type: ignore[operator]
    except (TypeError, KeyError):
        return None

    return _ChunkPlan(
        total_chunks=total,
        prefix_builder=lambda n: content[:n],  # type: ignore[operator]
        cache_discriminator=id(content),
    )


def _build_mapping_like_chunk_plan(content: object) -> _ChunkPlan | None:
    """Build chunk plan for mapping-like objects with items iteration.

    Args:
        content: Candidate mapping-like content.

    Returns:
        Chunk plan when mapping metadata is available, else ``None``.
    """
    if not _looks_like_mapping(content):
        return None

    try:
        total = len(content)  # type: ignore[arg-type]
        list(islice(content.items(), 1))  # type: ignore[union-attr]
    except (TypeError, AttributeError):
        return None

    if total <= 0:
        return None

    return _ChunkPlan(
        total_chunks=total,
        prefix_builder=lambda n: type(content)
        (islice(content.items(), n)),  # type: ignore[arg-type,call-arg]
        cache_discriminator=id(content),
    )


def _looks_like_mapping(content: object) -> bool:
    """Heuristically detect mapping-like protocol support.

    Args:
        content: Candidate content object.

    Returns:
        ``True`` when mapping-like attributes are present.
    """
    return hasattr(content, 'keys') and hasattr(content, '__getitem__') and hasattr(
        content, 'items')


def _has_deterministic_mapping_order(content: object) -> bool:
    """Check whether mapping iteration order is deterministic.

    Args:
        content: Candidate mapping-like content.

    Returns:
        ``True`` for mappings with deterministic key iteration.
    """
    return isinstance(content, dict)


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


def _find_prefix_size(
    *,
    draft_panel: Any,
    budget: _PanelPreviewBudget,
    plan: _ChunkPlan,
    probe_render: Callable[[Any], tuple[int, int]],
    memo: _PreviewPruningMemo,
    width_stabilization_window: int,
) -> int | None:
    viewport_cap = (budget.width_budget or 1) * (budget.height_budget or 1) + 1
    cap = min(viewport_cap, plan.total_chunks)
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
    cache_key = _probe_cache_key(draft_panel, plan, prefix_size)
    cached = memo.probe_cache.get(cache_key)
    if cached is not None:
        return cached

    prefix_panel = draft_panel.create_modified_copy(content=plan.prefix_builder(prefix_size))
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


def _probe_cache_key(draft_panel: Any, plan: _ChunkPlan,
                     prefix_size: int) -> tuple[int, int, int, int, int, int]:
    frame_hash = hash(draft_panel.frame)
    config_hash = hash(draft_panel.config)
    printer_hash = hash(getattr(draft_panel.config, 'printer', None))
    return (
        id(draft_panel.content),
        plan.cache_discriminator,
        prefix_size,
        frame_hash,
        config_hash,
        printer_hash,
    )


__all__ = ['_PreviewPruningMemo', '_effective_coarseness_threshold', '_maybe_prune_draft_panel']
