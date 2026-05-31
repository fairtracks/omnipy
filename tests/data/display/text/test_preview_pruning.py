from dataclasses import dataclass, field

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.preview_pruning import _maybe_prune_draft_panel, _PreviewPruningMemo


@dataclass(frozen=True)
class _FakeDraftPanel:
    content: object
    frame: Frame
    inner_frame: Frame
    config: OutputConfig = field(default_factory=OutputConfig)

    def create_modified_copy(
        self,
        content: object,
        frame: Frame | None = None,
        config: OutputConfig | None = None,
        **_kwargs,
    ) -> '_FakeDraftPanel':
        return _FakeDraftPanel(
            content=content,
            frame=frame or self.frame,
            inner_frame=self.inner_frame,
            config=config or self.config,
        )


def test_sequence_rendered_prefix_superset_stops_at_viewport() -> None:
    content = [f'item-{i}' for i in range(20)]
    panel = _FakeDraftPanel(
        content=content,
        frame=Frame(Dimensions(width=80, height=30)),
        inner_frame=Frame(Dimensions(width=18, height=4)),
    )

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, list)
        width = max((len(item) for item in prefix_panel.content), default=0)
        height = len(prefix_panel.content)
        return width, height

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert isinstance(pruned_panel.content, list)
    assert pruned_panel.content == content[:4]


def test_string_chunking_and_pruning() -> None:
    content = 'x' * 700
    panel = DraftPanel(content, frame=Frame(Dimensions(width=40, height=3)))

    def _probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, str)
        width = min(len(prefix_panel.content), 40)
        height = (len(prefix_panel.content) + 99) // 100
        return width, height

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert isinstance(pruned_panel.content, str)
    assert pruned_panel.content == content[:256]


def test_mapping_pruning_insertion_order() -> None:
    content = {f'k{i}': i for i in range(10)}
    panel = DraftPanel(content, frame=Frame(Dimensions(width=20, height=3)))

    def _probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, dict)
        width = max((len(key) for key in prefix_panel.content), default=0)
        height = len(prefix_panel.content)
        return width, height

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert isinstance(pruned_panel.content, dict)
    assert list(pruned_panel.content.items()) == list(content.items())[:3]


def test_probe_caps_and_fallback() -> None:
    unbounded_width_panel = DraftPanel(
        list(range(1000)),
        frame=Frame(Dimensions(width=None, height=5)),
    )
    bounded_width_panel = DraftPanel(
        list(range(1000)),
        frame=Frame(Dimensions(width=20, height=None)),
    )

    probe_calls = 0

    def _unstable_probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        nonlocal probe_calls
        probe_calls += 1
        assert isinstance(prefix_panel.content, list)
        size = len(prefix_panel.content)
        return size, size

    unbounded_result = _maybe_prune_draft_panel(
        unbounded_width_panel,
        probe_render=_unstable_probe_render,
        max_probe_items=16,
    )

    assert unbounded_result is unbounded_width_panel
    assert probe_calls == 0

    bounded_result = _maybe_prune_draft_panel(
        bounded_width_panel,
        probe_render=_unstable_probe_render,
        max_probe_items=16,
    )

    assert bounded_result is bounded_width_panel
    assert probe_calls > 0


def test_probe_cache_effectiveness() -> None:
    panel = DraftPanel(
        [f'item-{i}' for i in range(128)],
        frame=Frame(Dimensions(width=24, height=6)),
    )

    probe_calls = 0

    def _probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        nonlocal probe_calls
        probe_calls += 1
        assert isinstance(prefix_panel.content, list)
        width = max((len(item) for item in prefix_panel.content), default=0)
        height = len(prefix_panel.content)
        return width, height

    memo = _PreviewPruningMemo()
    first_result = _maybe_prune_draft_panel(panel, probe_render=_probe_render, memo=memo)
    calls_after_first_run = probe_calls
    second_result = _maybe_prune_draft_panel(panel, probe_render=_probe_render, memo=memo)

    assert calls_after_first_run > 0
    assert probe_calls == calls_after_first_run
    assert second_result.content == first_result.content

    _maybe_prune_draft_panel(panel, probe_render=_probe_render, memo=_PreviewPruningMemo())

    assert probe_calls > calls_after_first_run
