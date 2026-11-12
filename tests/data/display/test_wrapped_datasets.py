from unittest.mock import Mock

import pytest
import pytest_cases as pc

from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._mixins.display import BaseDisplayMixin
from omnipy.data.dataset import Dataset, is_dataset_instance
from omnipy.data.model import Model
from omnipy.shared.enums.display import DocsDisplayMethod
from omnipy.shared.enums.ui import UserInterfaceType

from .cases import wrapped_datasets
from .helpers.classes import IntegerDataset, WrappedDatasetCase, WrappedIntegerDataset


@pc.parametrize_with_cases('case', cases=wrapped_datasets)
def test_dataset_property_resolves_through_mimicking(
    case: WrappedDatasetCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    revalidate = Mock(side_effect=AssertionError('Property access revalidated a Model'))
    monkeypatch.setattr(Model, '_validate_and_set_value', revalidate)

    dataset = getattr(case.wrapped, 'dataset')

    assert is_dataset_instance(dataset)
    assert dataset.dataset is dataset
    assert dataset == case.dataset
    revalidate.assert_not_called()


@pytest.mark.parametrize('method', ['default', 'peek', 'full', 'json'])
@pc.parametrize_with_cases('case', cases=wrapped_datasets)
def test_wrapped_dataset_docs(case: WrappedDatasetCase, method: DocsDisplayMethod.Literals) -> None:
    assert case.wrapped._docs(method=method) == case.dataset._docs(method=method)


@pc.parametrize_with_cases('case', cases=wrapped_datasets)
def test_wrapped_dataset_preview_titles(case: WrappedDatasetCase) -> None:
    panel = case.wrapped.peek(inner_titles=['First', 'Second'], return_draft_panel=True)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert list(panel.content) == ['0. first', '1. second']
    assert [child.title for child in panel.content.values()] == ['First', 'Second']


@pc.parametrize_with_cases('case', cases=wrapped_datasets)
def test_wrapped_dataset_inside_dataset(case: WrappedDatasetCase) -> None:
    dataset = Dataset[Model[object]](group=case.wrapped)

    panel = dataset.peek(return_draft_panel=True)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    child = panel.content['0. group']
    assert isinstance(child.content, Layout)
    assert list(child.content) == ['0. first', '1. second']


@pc.parametrize_with_cases('case', cases=wrapped_datasets)
def test_wrapped_dataset_browse(case: WrappedDatasetCase, monkeypatch: pytest.MonkeyPatch) -> None:
    browse = Mock()
    monkeypatch.setattr(Dataset, '_browse', browse)
    monkeypatch.setattr(
        BaseDisplayMixin,
        '_browse_nested_content',
        Mock(side_effect=AssertionError('Dataset browse was not used')),
    )

    case.wrapped.browse(ui=UserInterfaceType.BROWSER_PAGE)

    browse.assert_called_once_with(ui=UserInterfaceType.BROWSER_PAGE)


def test_nested_model_keeps_outer_title() -> None:
    model = Model[Model[int]](1)

    panel = model.peek(return_draft_panel=True)

    assert isinstance(panel, DraftPanel)
    assert isinstance(panel.content, Layout)
    assert list(panel.content) == ['Model[Model[int]]']


def test_union_display_follows_current_content() -> None:
    dataset = IntegerDataset(first=1, second=2)
    model = Model[WrappedIntegerDataset | int](dataset)

    assert model._docs() == dataset._docs()

    model.content = 42

    assert getattr(model, 'dataset', None) is None
    output = model._docs()
    assert isinstance(output, str)
    assert 'Data file name' not in output

    model.content = WrappedIntegerDataset(dataset)

    assert model._docs() == dataset._docs()


def test_empty_dataset_in_optional_model() -> None:
    dataset = IntegerDataset()
    model = Model[IntegerDataset | None](dataset)

    assert model._docs() == dataset._docs()

    model.content = None

    assert getattr(model, 'dataset', None) is None
    output = model._docs()
    assert isinstance(output, str)
    assert 'Data file name' not in output
