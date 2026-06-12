from collections import OrderedDict
from dataclasses import dataclass, field

from omnipy.components.json.models import JsonModel
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.text.preview_pruning import (_build_chunk_plan,
                                                       _effective_coarseness_threshold,
                                                       _maybe_prune_draft_panel,
                                                       _PreviewPruningMemo,
                                                       _probe_prefix)
from omnipy.shared.enums.display import PrettyPrinterLib


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


class _SliceableListWrapper:
    def __init__(self, data: list[object]) -> None:
        self._data = data

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: slice | int) -> object:
        if isinstance(key, slice):
            return _SliceableListWrapper(self._data[key])
        return self._data[key]


class _LenUnavailableSequence:
    def __init__(self, data: list[object]) -> None:
        self._data = data

    def __len__(self) -> int:
        raise TypeError('len() unavailable')

    def __getitem__(self, key: slice | int) -> object:
        return self._data[key]


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
    assert pruned_panel.content == content[:512]


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
    assert list(pruned_panel.content.items()) == list(content.items())[:4]


def test_ordered_dict_pruning_preserves_mapping_type() -> None:
    content = OrderedDict((f'k{i}', i) for i in range(10))
    panel = DraftPanel(content, frame=Frame(Dimensions(width=20, height=3)))

    def _probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, OrderedDict)
        width = max((len(str(key)) for key in prefix_panel.content.keys()), default=0)
        height = len(prefix_panel.content)
        return width, height

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert pruned_panel is not panel
    assert isinstance(pruned_panel.content, OrderedDict)
    assert list(pruned_panel.content.items()) == list(content.items())[:4]


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
    unstable_probe_sizes: list[int] = []

    def _unstable_probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        nonlocal probe_calls
        probe_calls += 1
        assert isinstance(prefix_panel.content, list)
        size = len(prefix_panel.content)
        unstable_probe_sizes.append(size)
        return size, size

    unbounded_result = _maybe_prune_draft_panel(
        unbounded_width_panel,
        probe_render=_unstable_probe_render,
    )

    assert unbounded_result is not unbounded_width_panel
    assert probe_calls > 0

    bounded_result = _maybe_prune_draft_panel(
        bounded_width_panel,
        probe_render=_unstable_probe_render,
    )

    assert bounded_result is bounded_width_panel
    assert probe_calls > 0
    assert max(unstable_probe_sizes) <= 21

    binary_search_probe_sizes: list[int] = []

    def _binary_search_probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, list)
        size = len(prefix_panel.content)
        binary_search_probe_sizes.append(size)
        return size, size

    # With height=5, probe stops by height at n=8 (height=8 > 5),
    # binary searches between 4 and 8.
    _maybe_prune_draft_panel(
        DraftPanel(
            list(range(1000)),
            frame=Frame(Dimensions(width=20, height=5)),
        ),
        probe_render=_binary_search_probe_render,
    )

    assert max(binary_search_probe_sizes) <= 21


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


def test_probe_cache_key_distinguishes_chunk_plans_for_same_prefix_size() -> None:
    panel = _FakeDraftPanel(
        content=['root'],
        frame=Frame(Dimensions(width=40, height=10)),
        inner_frame=Frame(Dimensions(width=40, height=10)),
    )

    flat_plan = _build_chunk_plan(list(range(8)))
    nested_plan = _build_chunk_plan([[i] for i in range(8)])
    assert flat_plan is not None
    assert nested_plan is not None

    probe_calls = 0

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        nonlocal probe_calls
        probe_calls += 1
        assert isinstance(prefix_panel.content, list)

        if prefix_panel.content and isinstance(prefix_panel.content[0], list):
            return 1, 100 + len(prefix_panel.content)

        return 1, len(prefix_panel.content)

    memo = _PreviewPruningMemo()
    flat_result = _probe_prefix(
        draft_panel=panel,
        plan=flat_plan,
        prefix_size=3,
        probe_render=_probe_render,
        memo=memo,
    )
    nested_result = _probe_prefix(
        draft_panel=panel,
        plan=nested_plan,
        prefix_size=3,
        probe_render=_probe_render,
        memo=memo,
    )

    assert flat_result != nested_result
    assert probe_calls == 2


def test_panel_cache_distinguishes_configs_for_same_content_and_frame() -> None:
    content = [f'item-{i}' for i in range(20)]
    frame = Frame(Dimensions(width=80, height=4))

    rich_panel = _FakeDraftPanel(
        content=content,
        frame=frame,
        inner_frame=frame,
        config=OutputConfig(printer=PrettyPrinterLib.RICH),
    )
    devtools_panel = _FakeDraftPanel(
        content=content,
        frame=frame,
        inner_frame=frame,
        config=OutputConfig(printer=PrettyPrinterLib.DEVTOOLS),
    )

    probe_sizes: dict[str, list[int]] = {
        PrettyPrinterLib.RICH: [],
        PrettyPrinterLib.DEVTOOLS: [],
    }

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, list)
        size = len(prefix_panel.content)
        printer = prefix_panel.config.printer
        probe_sizes[printer].append(size)

        if printer == PrettyPrinterLib.RICH:
            return 1, size

        return 1, size // 2

    memo = _PreviewPruningMemo()
    rich_result = _maybe_prune_draft_panel(rich_panel, probe_render=_probe_render, memo=memo)
    devtools_result = _maybe_prune_draft_panel(
        devtools_panel, probe_render=_probe_render, memo=memo)

    assert isinstance(rich_result.content, list)
    assert isinstance(devtools_result.content, list)
    assert rich_result.content != devtools_result.content
    assert probe_sizes[PrettyPrinterLib.RICH]
    assert probe_sizes[PrettyPrinterLib.DEVTOOLS]


def test_json_model_with_nested_model_wrapper_is_prunable() -> None:
    panel = DraftPanel(
        JsonModel(list(range(10000))),
        frame=Frame(Dimensions(width=20, height=4)),
    )

    probe_calls = 0

    def _probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        nonlocal probe_calls
        probe_calls += 1

        assert isinstance(prefix_panel.content, JsonModel)
        pruned_content = prefix_panel.content.to_data()
        assert isinstance(pruned_content, list)
        return 10, len(pruned_content)

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert probe_calls > 0
    assert pruned_panel is not panel
    assert isinstance(pruned_panel.content, JsonModel)
    assert isinstance(pruned_panel.content.content, type(panel.content.content))
    pruned_data = pruned_panel.content.to_data()
    assert isinstance(pruned_data, list)
    assert len(pruned_data) == 4


def test_duck_typed_sliceable_content_is_prunable() -> None:
    panel = DraftPanel(
        _SliceableListWrapper(list(range(1000))),
        frame=Frame(Dimensions(width=20, height=4)),
    )

    def _probe_render(prefix_panel: DraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, _SliceableListWrapper)
        return 10, len(prefix_panel.content)

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert isinstance(pruned_panel.content, _SliceableListWrapper)
    assert len(pruned_panel.content) == 4


def test_effective_coarseness_threshold_formula() -> None:
    assert _effective_coarseness_threshold(height_budget=10, width_stabilization_window=2) == 8
    assert _effective_coarseness_threshold(height_budget=1, width_stabilization_window=1) == 4
    assert _effective_coarseness_threshold(height_budget=None, width_stabilization_window=2) == 7


def test_hierarchical_skip_level_descent_prunes_deep_single_chain() -> None:
    content = [[[i for i in range(60)]]]
    panel = _FakeDraftPanel(
        content=content,
        frame=Frame(Dimensions(width=30, height=7)),
        inner_frame=Frame(Dimensions(width=30, height=4)),
    )

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, list)

        if prefix_panel.content and isinstance(prefix_panel.content[0], list):
            if prefix_panel.content[0] and isinstance(prefix_panel.content[0][0], list):
                nested_len = len(prefix_panel.content[0][0])
                return nested_len, nested_len

            child_len = len(prefix_panel.content[0])
            return child_len, child_len

        root_len = len(prefix_panel.content)
        return root_len, root_len

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert isinstance(pruned_panel.content, list)
    assert len(pruned_panel.content) == 1
    assert isinstance(pruned_panel.content[0], list)
    assert isinstance(pruned_panel.content[0][0], list)
    assert len(pruned_panel.content[0][0]) == 5


def test_hierarchical_three_by_many_selects_finer_granularity() -> None:
    content = [[row * 100 + col for col in range(80)] for row in range(3)]
    panel = _FakeDraftPanel(
        content=content,
        frame=Frame(Dimensions(width=30, height=7)),
        inner_frame=Frame(Dimensions(width=30, height=4)),
    )

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, list)
        if prefix_panel.content and isinstance(prefix_panel.content[0], list):
            child_len = len(prefix_panel.content[0])
            return child_len, child_len

        root_len = len(prefix_panel.content)
        return root_len, root_len

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert isinstance(pruned_panel.content, list)
    assert len(pruned_panel.content) == 1
    assert isinstance(pruned_panel.content[0], list)
    assert len(pruned_panel.content[0]) == 5


def test_hierarchical_parent_restart_when_deep_path_underfills() -> None:
    content = [[i] for i in range(30)]
    panel = _FakeDraftPanel(
        content=content,
        frame=Frame(Dimensions(width=30, height=50)),
        inner_frame=Frame(Dimensions(width=30, height=40)),
    )

    root_probe_count = 0
    child_probe_count = 0

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        nonlocal root_probe_count, child_probe_count
        assert isinstance(prefix_panel.content, list)

        if prefix_panel.content and isinstance(prefix_panel.content[0], list):
            root_probe_count += 1
            return 1, len(prefix_panel.content) * 2

        child_probe_count += 1
        return 1, len(prefix_panel.content) // 2

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert child_probe_count > 0
    assert root_probe_count > 0
    assert isinstance(pruned_panel.content, list)
    assert len(pruned_panel.content) == 21


def test_fail_open_when_child_cheap_metadata_is_unavailable() -> None:
    content = [
        _LenUnavailableSequence(list(range(20))),
        [1],
        [2],
        [3],
        [4],
        [5],
    ]
    panel = _FakeDraftPanel(
        content=content,
        frame=Frame(Dimensions(width=30, height=14)),
        inner_frame=Frame(Dimensions(width=30, height=8)),
    )

    def _probe_render(prefix_panel: _FakeDraftPanel) -> tuple[int, int]:
        assert isinstance(prefix_panel.content, list)
        return 1, len(prefix_panel.content) * 2

    pruned_panel = _maybe_prune_draft_panel(panel, probe_render=_probe_render)

    assert pruned_panel is panel
