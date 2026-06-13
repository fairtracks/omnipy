from typing import Any

import pytest

from omnipy import Dataset, Model, PrettyPrinterLib, UserInterfaceType
from omnipy.components.json.models import is_json_model_instance_hack
from omnipy.data._display.text import pretty as pretty_module

from .helpers import render_panel_to_plain_terminal


def test_model_peek_preview_pruning_preserves_viewport_and_skips_hidden_tail(
        monkeypatch: pytest.MonkeyPatch) -> None:
    class _TrackedItem:
        touched_indices: set[int] = set()

        def __init__(self, idx: int) -> None:
            self.idx = idx

        def __repr__(self) -> str:
            _TrackedItem.touched_indices.add(self.idx)
            return f'item-{self.idx:03}'

    model = Model[list[_TrackedItem]]([_TrackedItem(i) for i in range(180)])

    _TrackedItem.touched_indices.clear()
    with monkeypatch.context() as patch_ctx:
        patch_ctx.setattr(
            pretty_module,
            '_maybe_prune_draft_panel',
            lambda draft_panel, *, probe_render, memo: draft_panel,
        )
        unpruned_output = render_panel_to_plain_terminal(
            model._peek(
                width=26,
                height=7,
                ui=UserInterfaceType.TERMINAL,
                printer=PrettyPrinterLib.RICH,
                freedom=0,
            ))
    unpruned_max_touched_idx = max(_TrackedItem.touched_indices)

    _TrackedItem.touched_indices.clear()
    pruned_output = render_panel_to_plain_terminal(
        model._peek(
            width=26,
            height=7,
            ui=UserInterfaceType.TERMINAL,
            printer=PrettyPrinterLib.RICH,
            freedom=0,
        ))
    pruned_max_touched_idx = max(_TrackedItem.touched_indices)

    assert pruned_output == unpruned_output
    assert unpruned_max_touched_idx == 179
    assert pruned_max_touched_idx < unpruned_max_touched_idx


def test_model_peek_preview_pruning_memo_is_per_top_level_render_call(
        monkeypatch: pytest.MonkeyPatch) -> None:
    model = Model[list[int]](list(range(180)))

    observed_memos: list[object] = []
    original_maybe_prune = getattr(pretty_module, '_maybe_prune_draft_panel')

    def _track_memo(draft_panel, *, probe_render, memo):
        observed_memos.append(memo)
        return original_maybe_prune(draft_panel, probe_render=probe_render, memo=memo)

    monkeypatch.setattr(pretty_module, '_maybe_prune_draft_panel', _track_memo)

    render_panel_to_plain_terminal(
        model._peek(
            width=26,
            height=7,
            ui=UserInterfaceType.TERMINAL,
            printer=PrettyPrinterLib.RICH,
            freedom=0,
        ))
    render_panel_to_plain_terminal(
        model._peek(
            width=26,
            height=7,
            ui=UserInterfaceType.TERMINAL,
            printer=PrettyPrinterLib.RICH,
            freedom=0,
        ))

    assert len(observed_memos) >= 2
    assert observed_memos[0] is not observed_memos[1]


def test_model_json_preview_pruning_triggers_for_large_json_list(
        monkeypatch: pytest.MonkeyPatch) -> None:
    model = Model[list[int]](range(10000))

    observed_pruned_json_model_panel = False
    original_maybe_prune = getattr(pretty_module, '_maybe_prune_draft_panel')

    def _track_json_model_panel_pruning(draft_panel, *, probe_render, memo):
        nonlocal observed_pruned_json_model_panel

        out_panel = original_maybe_prune(draft_panel, probe_render=probe_render, memo=memo)
        if is_json_model_instance_hack(draft_panel.content):
            if out_panel is not draft_panel:
                observed_pruned_json_model_panel = True

        return out_panel

    monkeypatch.setattr(pretty_module, '_maybe_prune_draft_panel', _track_json_model_panel_pruning)

    render_panel_to_plain_terminal(
        model._json(
            width=24,
            height=8,
            ui=UserInterfaceType.TERMINAL,
            printer=PrettyPrinterLib.RICH,
            freedom=0,
            debug=False,
        ))

    assert observed_pruned_json_model_panel is True


def test_model_json_verbose_prune_logs_reduced_preparation(
        capsys: pytest.CaptureFixture[str]) -> None:
    import omnipy.shared.constants as const

    model = Model[list[int]](range(10000))

    const.VERBOSE_PRUNE = True
    try:
        model.json()
        captured = capsys.readouterr()
    finally:
        const.VERBOSE_PRUNE = False

    prune_lines = [line for line in captured.out.splitlines() if line.startswith('[PRUNE] ')]
    assert prune_lines

    pruned_lines = [line for line in prune_lines if line.startswith('[PRUNE] Pruned: ')]
    assert pruned_lines

    pruned_line_payload = pruned_lines[-1].split(' | ', maxsplit=1)[0]
    before_after_text = pruned_line_payload.removeprefix('[PRUNE] Pruned: ').removesuffix(' items')
    before_text, after_text = before_after_text.split(' -> ', maxsplit=1)

    assert int(before_text) == 10000
    assert int(after_text) < int(before_text)


def test_dataset_list_bounded_height_materializes_only_front_rows(
        monkeypatch: pytest.MonkeyPatch) -> None:
    dataset = Dataset[Model[list[int]]]({f'row_{i}': [i, i + 1] for i in range(30)})

    len_calls = 0
    size_calls = 0
    materialized_row_counts: list[int] = []

    def _track_len(cls, obj: Any) -> int | str:
        nonlocal len_calls
        len_calls += 1
        return 2

    def _track_size(cls, obj: Any) -> str:
        nonlocal size_calls
        size_calls += 1
        return '1 Byte'

    original_rows_to_materialize = type(dataset)._dataset_list_rows_to_materialize

    def _track_rows_to_materialize(instance, dataset_arg, frame, config) -> int:
        rows_to_materialize = original_rows_to_materialize(instance, dataset_arg, frame, config)
        materialized_row_counts.append(rows_to_materialize)
        return rows_to_materialize

    monkeypatch.setattr(type(dataset), '_len_if_available', classmethod(_track_len))
    monkeypatch.setattr(type(dataset), '_obj_size_if_available', classmethod(_track_size))
    monkeypatch.setattr(
        type(dataset), '_dataset_list_rows_to_materialize', classmethod(_track_rows_to_materialize))

    rendered_output = render_panel_to_plain_terminal(
        dataset._list(
            width=80,
            height=9,
            ui=UserInterfaceType.TERMINAL,
        ))

    assert materialized_row_counts
    assert materialized_row_counts[-1] == 6
    assert len_calls == materialized_row_counts[-1]
    assert size_calls == materialized_row_counts[-1]

    # Visible output stays unchanged
    assert '│ 0 │ row_0' in rendered_output
    assert '│ 1 │ row_1' in rendered_output
    assert '│ 2 │ row_2' in rendered_output
    assert '│ 3 │ row_3' in rendered_output
    assert '│ … │ …' in rendered_output
    assert 'row_4' not in rendered_output


def test_dataset_list_unbounded_height_still_materializes_all_rows(
        monkeypatch: pytest.MonkeyPatch) -> None:
    dataset = Dataset[Model[list[int]]]({f'row_{i}': [i, i + 1] for i in range(12)})

    len_calls = 0
    size_calls = 0
    materialized_row_counts: list[int] = []

    def _track_len(cls, obj: Any) -> int | str:
        nonlocal len_calls
        len_calls += 1
        return 2

    def _track_size(cls, obj: Any) -> str:
        nonlocal size_calls
        size_calls += 1
        return '1 Byte'

    original_rows_to_materialize = type(dataset)._dataset_list_rows_to_materialize

    def _track_rows_to_materialize(instance, dataset_arg, frame, config) -> int:
        rows_to_materialize = original_rows_to_materialize(instance, dataset_arg, frame, config)
        materialized_row_counts.append(rows_to_materialize)
        return rows_to_materialize

    monkeypatch.setattr(type(dataset), '_len_if_available', classmethod(_track_len))
    monkeypatch.setattr(type(dataset), '_obj_size_if_available', classmethod(_track_size))
    monkeypatch.setattr(
        type(dataset), '_dataset_list_rows_to_materialize', classmethod(_track_rows_to_materialize))

    rendered_output = render_panel_to_plain_terminal(
        dataset._list(
            width=80,
            height=None,
            ui=UserInterfaceType.TERMINAL,
        ))

    assert materialized_row_counts
    assert materialized_row_counts[-1] == len(dataset)
    assert len_calls == len(dataset)
    assert size_calls == len(dataset)
    assert '│ 11 │ row_11' in rendered_output
