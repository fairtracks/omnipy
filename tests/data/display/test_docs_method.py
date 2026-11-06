from inspect import signature
from unittest.mock import Mock

import pytest

from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._mixins.display import BaseDisplayMixin
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.enums.display import DocsDisplayMethod
from omnipy.shared.enums.ui import UserInterfaceType


def test_docs_renders_dataset_list_by_default_and_peek_on_request() -> None:
    dataset = Dataset[Model[list[int]]](first=[1, 2], second=[3])

    default_output = dataset._docs()
    peek_output = dataset._docs(method='peek')

    assert isinstance(default_output, str)
    assert isinstance(peek_output, str)
    assert 'Data file name' in default_output
    assert 'Data file name' not in peek_output
    assert 'first' in peek_output
    assert 'second' in peek_output


@pytest.mark.parametrize('method', ['default', 'peek', 'full', 'json'])
def test_docs_returns_selected_draft_without_rendering(
    method: DocsDisplayMethod.Literals, monkeypatch: pytest.MonkeyPatch
) -> None:
    dataset = Dataset[Model[int]](first=1, second=2)
    render = Mock(side_effect=AssertionError('draft panel was rendered'))
    monkeypatch.setattr(DraftPanel, 'render_next_stage', render)

    panel = dataset._docs(method=method, return_draft_panel=True, height=10)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert panel.config.ui == UserInterfaceType.BROWSER_TAG
    assert panel.frame.dims.height == (None if method == 'full' else 10)
    if method == 'default':
        assert 'Data file name' in panel.content
    elif method in ('peek', 'full'):
        assert list(panel.content) == ['0. first', '1. second']
    else:
        assert len(panel.content) == 1
    render.assert_not_called()


@pytest.mark.parametrize('wrap_dataset', [False, True])
def test_docs_default_draft_for_model(wrap_dataset: bool) -> None:
    model = Model[Dataset[Model[int]]]({'first': 1}) if wrap_dataset else Model[int](1)

    panel = model._docs(return_draft_panel=True)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert ('Data file name' in panel.content) == wrap_dataset


def test_docs_draft_accepts_preview_titles_and_ui() -> None:
    dataset = Dataset[Model[int]](first=1, second=2)

    panel = dataset._docs(
        method='peek',
        inner_titles=['Title'],
        return_draft_panel=True,
        ui=UserInterfaceType.TERMINAL,
    )

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert panel.content['0. first'].title == 'Title'
    assert panel.config.ui == UserInterfaceType.TERMINAL


def test_docs_draft_rejects_titles_for_default_dataset_list() -> None:
    with pytest.raises(TypeError, match='inner_titles'):
        Dataset[Model[int]](first=1)._docs(inner_titles=['Title'], return_draft_panel=True)


@pytest.mark.parametrize('return_draft_panel', [False, True])
def test_docs_normalizes_titles_once(
    return_draft_panel: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    normalize = Mock(wraps=BaseDisplayMixin._normalize_inner_titles)
    monkeypatch.setattr(BaseDisplayMixin, '_normalize_inner_titles', staticmethod(normalize))

    Model[int](1)._docs(inner_titles=['Title'], return_draft_panel=return_draft_panel)

    assert normalize.call_count == 1


def test_docs_false_draft_flag_and_signature() -> None:
    model = Model[int](1)

    assert model._docs(return_draft_panel=False) == model._docs()
    assert signature(model._docs).parameters['return_draft_panel'].default is False


def test_docs_returns_terminal_output_without_displaying(
    capsys: pytest.CaptureFixture[str],
) -> None:
    model = Model[int](1)

    model.peek(ui=UserInterfaceType.TERMINAL)
    expected = capsys.readouterr().out
    output = model._docs(method='peek', ui=UserInterfaceType.TERMINAL)

    assert isinstance(output, str)
    assert expected == output + '\n'
    assert capsys.readouterr().out == ''


def test_docs_passes_explicit_ui_to_renderer(monkeypatch: pytest.MonkeyPatch) -> None:
    render = Mock(return_value='rendered')
    monkeypatch.setattr(BaseDisplayMixin, '_display_according_to_ui_type', render)

    output = Model[int](1)._docs(ui=UserInterfaceType.AUTO)

    assert output == 'rendered'
    assert render.call_args.kwargs['ui_type'] == UserInterfaceType.AUTO
    assert render.call_args.kwargs['return_output_if_str'] is True


def test_docs_draft_flag_requires_bool() -> None:
    with pytest.raises(TypeError, match='return_draft_panel must be a bool'):
        Model[int](1)._docs(return_draft_panel='yes')  # type: ignore[arg-type]
