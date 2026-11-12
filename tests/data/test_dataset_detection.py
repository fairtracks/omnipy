"""Dataset detection through mimicking and the original direct type-check fallback."""

from unittest.mock import Mock

import pytest
import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.data.dataset import is_dataset_instance, is_dataset_subclass
from omnipy.data.model import is_model_of_dataset_instance, is_model_of_dataset_subclass, Model
from omnipy.shared.typedefs import TypeForm

from .display.cases import wrapped_datasets
from .display.helpers.classes import WrappedDatasetCase


@pc.parametrize_with_cases('case', cases=wrapped_datasets)
def test_detect_current_dataset(case: WrappedDatasetCase) -> None:
    assert is_model_of_dataset_instance(case.wrapped)
    dataset = getattr(case.wrapped, 'dataset')
    assert dataset == case.dataset
    assert dataset.dataset is dataset
    assert is_dataset_instance(dataset)
    assert not is_model_of_dataset_instance(dataset)


@pytest.mark.parametrize(
    'type_form, expected',
    [
        (JsonDataset, False),
        (Model[JsonDataset], True),
        (Model[Model[JsonDataset | int]], True),
        (Model[int | JsonDataset], False),
        (Model[int], False),
        (int | str, False),
    ],
)
def test_detect_default_dataset(type_form: TypeForm, expected: bool) -> None:
    assert is_model_of_dataset_subclass(type_form) is expected


@pytest.mark.parametrize(
    'model_cls, expected',
    [(Model[JsonDataset], True), (Model[Model[JsonDataset]], False), (Model[int], False)],
)
@pytest.mark.parametrize('error', [TypeError, ValueError])
def test_failed_construction_uses_only_original_direct_type_check(
    model_cls: type[Model], expected: bool, error: type[Exception], monkeypatch: pytest.MonkeyPatch
) -> None:
    constructor = Mock(side_effect=error('Default construction rejected'))
    monkeypatch.setattr(model_cls, '__init__', constructor)

    assert is_model_of_dataset_subclass(model_cls) is expected
    constructor.assert_called_once()


def test_default_branch_does_not_override_live_content() -> None:
    model = Model[int | JsonDataset](JsonDataset())
    assert is_model_of_dataset_instance(model)
    assert not is_model_of_dataset_subclass(type(model))
    assert not is_model_of_dataset_instance(Model[int]())


@pytest.mark.parametrize('dataset_cls', [JsonDataset])
def test_dataset_subclass_is_distinct_from_model_of_dataset(dataset_cls: TypeForm) -> None:
    assert is_dataset_subclass(dataset_cls)
    assert not is_model_of_dataset_subclass(dataset_cls)


def test_instance_detection_follows_current_union_content() -> None:
    model = Model[JsonDataset | int](JsonDataset())
    assert is_model_of_dataset_instance(model)

    model.content = 42
    assert not is_model_of_dataset_instance(model)

    model.content = JsonDataset()
    assert is_model_of_dataset_instance(model)
