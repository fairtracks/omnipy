from inspect import signature
from typing import assert_type, TYPE_CHECKING
from unittest.mock import Mock

import pytest

from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._mixins.display import BaseDisplayMixin
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.enums.display import DocsDisplayMethod
from omnipy.shared.enums.ui import UserInterfaceType
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    from reacton.core import Element

    from omnipy.shared.enums.ui import (
        BrowserUserInterfaceType,
        SpecifiedUserInterfaceType,
        TerminalOutputUserInterfaceType,
    )

    def _assert_draft_return_types(
        mixin: BaseDisplayMixin,
        ui_type: SpecifiedUserInterfaceType.Literals,
        str_ui_type: TerminalOutputUserInterfaceType.Literals | BrowserUserInterfaceType.Literals,
        return_draft_panel: bool,
    ) -> None:
        assert_type(
            mixin._display_or_return_draft(
                mixin._peek, ui_type=ui_type, return_draft_panel=return_draft_panel
            ),
            DraftPanel | Element | None,
        )
        assert_type(
            mixin._display_or_return_draft(
                mixin._peek,
                ui_type=str_ui_type,
                return_output_if_str=True,
                return_draft_panel=return_draft_panel,
            ),
            DraftPanel | str,
        )


@pytest.mark.parametrize('method', ['peek', 'full', 'json'])
@pytest.mark.parametrize('titles', [['Values'], ('Values',)])
def test_model_preview_inner_title(
    method: str, titles: list[str] | tuple[str, ...], capsys: pytest.CaptureFixture[str]
) -> None:
    model = Model[list[int]]([1, 2])

    getattr(model, method)(inner_titles=titles, ui=UserInterfaceType.TERMINAL)

    output = capsys.readouterr().out
    assert 'Values' in output
    assert 'Model[list[int]]' not in output
    assert 'JsonModel' not in output


@pytest.mark.parametrize('method', ['peek', 'full'])
def test_dataset_preview_partial_inner_titles(method: str) -> None:
    dataset = Dataset[Model[int]](first=1, second=2, third=3)

    panel = getattr(dataset, method)(inner_titles=['First', ''], return_draft_panel=True)

    assert [child.title for child in panel.content.values()] == ['First', '', '2. third']
    assert list(panel.content) == ['0. first', '1. second', '2. third']


def test_dataset_preview_renders_each_title(capsys: pytest.CaptureFixture[str]) -> None:
    dataset = Dataset[Model[int]](first=1, second=2)

    dataset.peek(inner_titles=['Alpha', 'Beta'], ui=UserInterfaceType.TERMINAL, width=100)

    output = capsys.readouterr().out
    assert 'Alpha' in output
    assert 'Beta' in output
    assert 'first' not in output
    assert 'second' not in output


def test_default_and_empty_title_overrides(capsys: pytest.CaptureFixture[str]) -> None:
    model = Model[int](1)

    model.peek(ui=UserInterfaceType.TERMINAL)
    default_output = capsys.readouterr().out
    model.peek(inner_titles=[], ui=UserInterfaceType.TERMINAL)
    assert capsys.readouterr().out == default_output
    model.peek(inner_titles=None, ui=UserInterfaceType.TERMINAL)
    assert capsys.readouterr().out == default_output
    model.peek(inner_titles=[''], ui=UserInterfaceType.TERMINAL)
    assert 'Model[int]' not in capsys.readouterr().out


def test_inner_titles_apply_only_to_first_level() -> None:
    nested = Dataset[Model[Dataset[Model[int]]]](child={'value': 1})

    panel = nested.peek(inner_titles=['Outer child'], return_draft_panel=True)
    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    child = panel.content['0. child']

    assert child.title == 'Outer child'
    assert isinstance(child.content, Layout)
    assert child.content['0. value'].title == '0. value'


def test_model_wrapping_dataset_uses_dataset_titles() -> None:
    model = Model[Dataset[Model[int]]]({'first': 1, 'second': 2})

    panel = model.peek(inner_titles=['First'], return_draft_panel=True)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert [child.title for child in panel.content.values()] == ['First', '1. second']


@pytest.mark.parametrize('method', ['peek', 'full', 'json'])
def test_reject_extra_titles_before_cropping(method: str) -> None:
    dataset = Dataset[Model[int]](first=1, second=2)
    titles = ['A', 'B'] if method == 'json' else ['A', 'B', 'C']

    with pytest.raises(ValueError, match='titles for .* inner panels'):
        getattr(dataset, method)(inner_titles=titles, max_panels_hor=1)


def test_titles_for_cropped_panels_are_valid() -> None:
    dataset = Dataset[Model[int]](first=1, second=2, third=3)

    panel = dataset.peek(inner_titles=['A', 'B', 'C'], max_panels_hor=1, return_draft_panel=True)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert panel.content['0. first'].title == 'A'


@pytest.mark.parametrize('titles', ['', 'A', 42, object(), {'title': 'A'}, [object()], iter(['A'])])
def test_reject_invalid_inner_titles(titles: object) -> None:
    model = Model[int](1)

    with pytest.raises(pyd.ValidationError):
        model.peek(inner_titles=titles, return_draft_panel=True)  # type: ignore[arg-type]


@pytest.mark.parametrize('method', ['peek', 'full', 'json', '_docs'])
@pytest.mark.parametrize('return_draft_panel', [False, True])
def test_reject_single_string_title(method: str, return_draft_panel: bool) -> None:
    model = Model[int](1)

    with pytest.raises(pyd.ValidationError):
        getattr(model, method)(inner_titles='Title', return_draft_panel=return_draft_panel)


@pytest.mark.parametrize('titles', [[42], (42,)])
def test_inner_titles_coerces_values(titles: object) -> None:
    model = Model[int](1)

    panel = model.peek(inner_titles=titles, return_draft_panel=True)  # type: ignore[arg-type]

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert panel.content['Model[int]'].title == '42'


def test_tuple_titles(capsys: pytest.CaptureFixture[str]) -> None:
    dataset = Dataset[Model[int]](first=1, second=2)

    dataset.peek(inner_titles=('Alpha', 'Beta'), ui=UserInterfaceType.TERMINAL, width=100)

    output = capsys.readouterr().out
    assert 'Alpha' in output
    assert 'Beta' in output


def test_tuple_with_extra_titles_is_rejected() -> None:
    model = Model[int](1)

    with pytest.raises(ValueError, match='2 titles for 1 inner panels'):
        model.peek(inner_titles=('Alpha', 'Beta'))


@pytest.mark.parametrize('use_generator', [False, True])
def test_titles_survive_jupyter_rerender(
    use_generator: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    import reacton

    from omnipy.data._display.integrations.jupyter import components

    component = Mock(return_value=object())
    monkeypatch.setattr(components, 'ReactivelyResizingHtml', component)
    monkeypatch.setattr(reacton, 'display', Mock())
    dataset = Dataset[Model[int]](first=1, second=2)

    titles = (title for title in ('Alpha', 'Beta')) if use_generator else ('Alpha', 'Beta')
    dataset.peek(inner_titles=titles, ui=UserInterfaceType.JUPYTER)  # type: ignore[arg-type]

    kwargs = component.call_args.kwargs
    render_panel = kwargs['render_panel_method']
    reactive_kwargs = kwargs['reactive_kwargs'].value
    for _ in range(2):
        output = render_panel(**reactive_kwargs).plain.terminal
        assert 'Alpha' in output
        assert 'Beta' in output


def test_empty_dataset_rejects_nonempty_titles() -> None:
    dataset = Dataset[Model[int]]()

    panel = dataset.peek(inner_titles=[], return_draft_panel=True)
    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert len(panel.content) == 0
    with pytest.raises(ValueError, match='1 titles for 0 inner panels'):
        dataset.peek(inner_titles=['Title'], return_draft_panel=True)


@pytest.mark.parametrize('method', ['peek', 'full', 'json'])
def test_docs_preview_inner_titles(method: DocsDisplayMethod.Literals) -> None:
    dataset = Dataset[Model[int]](first=1, second=2)

    output = dataset._docs(method=method, inner_titles=['Values'], width=100)

    assert isinstance(output, str)
    assert 'Values' in output


def test_docs_default_model_preview_inner_title() -> None:
    output = Model[int](1)._docs(inner_titles=['Values'])
    assert isinstance(output, str)
    assert 'Values' in output


def test_docs_default_dataset_accepts_none_inner_titles() -> None:
    dataset = Dataset[Model[int]](first=1)
    assert dataset._docs(inner_titles=None) == dataset._docs()


def test_list_and_browse_do_not_accept_inner_titles() -> None:
    dataset = Dataset[Model[int]](first=1)

    with pytest.raises(TypeError, match='inner_titles'):
        dataset.list(inner_titles=['Name'])  # type: ignore[call-arg]
    with pytest.raises(TypeError, match='inner_titles'):
        dataset._docs(inner_titles=['Name'])
    with pytest.raises(TypeError, match='inner_titles'):
        Model[int](1).browse(inner_titles=['Name'])  # type: ignore[call-arg]


def test_preview_signatures_expose_inner_titles() -> None:
    model = Model[int](1)
    dataset = Dataset[Model[int]](first=1)

    for method in (model.peek, model.full, model.json, model._docs):
        assert signature(method).parameters['inner_titles'].default is None
    for method in (dataset.list, model.browse):
        assert 'inner_titles' not in signature(method).parameters


@pytest.mark.parametrize('method', ['peek', 'full', 'json', 'list'])
def test_return_draft_panel_without_display(
    method: str, capsys: pytest.CaptureFixture[str]
) -> None:
    dataset = Dataset[Model[int]](first=1)

    panel = getattr(dataset, method)(
        return_draft_panel=True, ui=UserInterfaceType.TERMINAL, width=80, height=10
    )

    assert isinstance(panel, DraftPanel)
    assert panel.frame.dims.width == 80
    assert panel.frame.dims.height == (None if method == 'full' else 10)
    assert panel.config.ui == UserInterfaceType.TERMINAL
    assert capsys.readouterr().out == ''


@pytest.mark.parametrize('return_draft_panel', [False, True])
def test_title_normalized_once(return_draft_panel: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    normalize = Mock(wraps=BaseDisplayMixin._normalize_inner_titles)
    monkeypatch.setattr(BaseDisplayMixin, '_normalize_inner_titles', staticmethod(normalize))
    dataset = Dataset[Model[int]](first=1)

    dataset.peek(inner_titles=['Title'], return_draft_panel=return_draft_panel)

    assert normalize.call_count == 1


@pytest.mark.parametrize('method', ['peek', 'full', 'json', 'list', '_docs'])
def test_return_draft_panel_is_explicit_keyword_only(method: str) -> None:
    dataset = Dataset[Model[int]](first=1)
    code = getattr(dataset, method).__func__.__code__
    keyword_only_params = code.co_varnames[
        code.co_argcount : code.co_argcount + code.co_kwonlyargcount
    ]

    assert 'return_draft_panel' in keyword_only_params
    if method == '_docs':
        assert 'method' in keyword_only_params


@pytest.mark.parametrize('method', ['peek', 'full', 'json', 'list', '_docs'])
def test_return_draft_panel_requires_bool(method: str) -> None:
    with pytest.raises(TypeError, match='return_draft_panel must be a bool'):
        getattr(Dataset[Model[int]](first=1), method)(return_draft_panel='yes')


def test_jupyter_draft_does_not_render_or_display(monkeypatch: pytest.MonkeyPatch) -> None:
    import reacton

    render = Mock(side_effect=AssertionError('draft panel was rendered'))
    display = Mock()
    monkeypatch.setattr(DraftPanel, 'render_next_stage', render)
    monkeypatch.setattr(reacton, 'display', display)

    panel = Model[int](1).peek(return_draft_panel=True, ui=UserInterfaceType.JUPYTER)

    assert isinstance(panel, DraftPanel)
    render.assert_not_called()
    display.assert_not_called()


def test_false_draft_flag_preserves_display(capsys: pytest.CaptureFixture[str]) -> None:
    model = Model[int](1)

    model.peek(ui=UserInterfaceType.TERMINAL)
    default_output = capsys.readouterr().out
    model.peek(ui=UserInterfaceType.TERMINAL, return_draft_panel=False)
    assert capsys.readouterr().out == default_output


def test_draft_flag_not_supported_by_browse() -> None:
    model = Model[int](1)

    with pytest.raises(TypeError, match='return_draft_panel'):
        model.browse(return_draft_panel=True)  # type: ignore[call-arg]
