"""Tests for general-purpose dataset and model creation tasks."""

from typing import Annotated, Generic

import pytest
from typing_extensions import TypeVar

from omnipy.components.general.tasks import (concat_all_vals_in_datasets_as_args,
                                             concat_all_vals_in_datasets_as_kwargs,
                                             create_dataset_from_args,
                                             create_dataset_from_kwargs,
                                             create_model_from_args,
                                             create_model_from_kwargs,
                                             union_all_datasets_as_args,
                                             union_all_datasets_as_kwargs,
                                             union_all_vals_in_datasets_as_args,
                                             union_all_vals_in_datasets_as_kwargs)
from omnipy.data.dataset import Dataset
from omnipy.data.model import is_model_instance, Model
from omnipy.data.param import (bind_adjust_dataset_func,
                               bind_adjust_model_func,
                               params_dataclass,
                               ParamsBase)
from omnipy.shared.protocols.hub.runtime import IsRuntime


class FloatModel(Model[float]):
    ...


class IntModel(Model[int]):
    ...


class _RoundedIntModel(Model[float | int]):
    @params_dataclass
    class Params(ParamsBase):
        round_to_nearest: bool = False

    @classmethod
    def _parse_data(cls, data: float | int) -> int:
        if isinstance(data, int):
            return data

        return round(data) if cls.Params.round_to_nearest else int(data)


class RoundedIntModel(_RoundedIntModel):
    adjust = bind_adjust_model_func(
        _RoundedIntModel.clone_model_cls,
        _RoundedIntModel.Params,
    )


class FloatDataset(Dataset[FloatModel]):
    ...


class IntDataset(Dataset[IntModel]):
    ...


RoundedIntModelT = TypeVar('RoundedIntModelT', bound=Model, default=RoundedIntModel)


class _RoundedIntDataset(Dataset[RoundedIntModelT], Generic[RoundedIntModelT]):
    ...


class RoundedIntDataset(_RoundedIntDataset[RoundedIntModel]):
    adjust = bind_adjust_dataset_func(
        _RoundedIntDataset[RoundedIntModel].clone_dataset_cls,
        RoundedIntModel,
        RoundedIntModel.Params,
    )


def test_create_dataset_from_args():
    """Create datasets from a single positional source dataset."""
    floats = FloatDataset(a=1.23, b=3.6)
    ints = create_dataset_from_args.run(floats, dataset_cls=IntDataset)
    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_from_args_with_default_params():
    """Create datasets using default adjustable parameters."""
    floats = FloatDataset(a=1.23, b=3.6)
    ints = create_dataset_from_args.run(floats, dataset_cls=RoundedIntDataset)
    assert isinstance(ints, RoundedIntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_from_args_with_params() -> None:
    """Create datasets using customized adjustable parameters."""
    RoundToNearestIntDataset = RoundedIntDataset.adjust(
        'RoundToNearestIntDataset', 'RoundToNearestIntModel', round_to_nearest=True)

    floats = FloatDataset(a=1.23, b=3.6)
    ints = create_dataset_from_args.run(floats, dataset_cls=RoundToNearestIntDataset)
    assert isinstance(ints, RoundToNearestIntDataset)
    assert ints.to_data() == dict(a=1, b=4)


def test_create_dataset_from_args_accepts_zero_positional_args() -> None:
    """Create an empty dataset when no positional arguments are provided."""
    ints = create_dataset_from_args.run(dataset_cls=IntDataset)

    assert isinstance(ints, IntDataset)
    assert ints.to_data() == {}


def test_create_dataset_from_args_accepts_multiple_positional_pairs() -> None:
    """Create datasets from multiple positional ``(key, value)`` pairs."""
    ints = create_dataset_from_args.run(('a', 1.23), ('b', 3.6), dataset_cls=IntDataset)

    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_from_args_with_key_single_arg() -> None:
    """Create a single-entry dataset using the ``key`` keyword argument."""
    ints = create_dataset_from_args.run(1.23, dataset_cls=IntDataset, key='a')

    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1)


def test_create_dataset_from_args_with_keys_multiple_args() -> None:
    """Create datasets from positional args using explicit ``keys``."""
    ints = create_dataset_from_args.run(1.23, 3.6, dataset_cls=IntDataset, keys=('a', 'b'))

    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_from_args_rejects_both_key_and_keys() -> None:
    """Reject configuring both ``key`` and ``keys`` at the same time."""
    with pytest.raises(AssertionError, match='Only one of `key` or `keys`'):
        create_dataset_from_args.run(1.23, dataset_cls=IntDataset, key='a', keys=('a',))


def test_create_dataset_from_args_rejects_keys_length_mismatch() -> None:
    """Reject explicit ``keys`` when length does not match positional args."""
    with pytest.raises(
            AssertionError, match='Number of keys must match number of positional arguments'):
        create_dataset_from_args.run(1.23, 3.6, dataset_cls=IntDataset, keys=('a',))


def test_create_dataset_from_args_rejects_keys_without_args() -> None:
    """Reject ``key``/``keys`` when there are no positional args to map."""
    with pytest.raises(AssertionError, match='No positional arguments were provided'):
        create_dataset_from_args.run(dataset_cls=IntDataset, key='a')

    with pytest.raises(AssertionError, match='No positional arguments were provided'):
        create_dataset_from_args.run(dataset_cls=IntDataset, keys=('a',))


def test_create_dataset_from_kwargs_from_models() -> None:
    """Create datasets from model instances supplied as kwargs."""
    ints = create_dataset_from_kwargs.run(
        dataset_cls=RoundedIntDataset,
        a=FloatModel(1.23),
        b=FloatModel(3.6),
    )

    assert isinstance(ints, RoundedIntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_from_kwargs_from_subdatasets() -> None:
    """Create nested datasets from sub-datasets supplied as kwargs."""
    nested_dataset = create_dataset_from_kwargs.run(
        dataset_cls=Dataset[Dataset[IntModel]],
        first=FloatDataset(a=1.23),
        second=FloatDataset(b=3.6),
    )

    assert isinstance(nested_dataset['first'], Dataset)
    assert nested_dataset.to_data() == dict(first=dict(a=1), second=dict(b=3))


def test_create_model_from_args_accepts_multiple_positional_args() -> None:
    """Create models from any number of positional args via tuple-style root input."""
    tuple_model = create_model_from_args.run(1.23, 3.6, model_cls=Model[tuple[int, ...]])

    assert tuple_model.to_data() == (1, 3)


def test_create_model_from_args_preserves_single_positional_arg() -> None:
    """Create models from a single positional arg without wrapping it in a tuple."""
    int_model = create_model_from_args.run(3.6, model_cls=IntModel)

    assert isinstance(int_model, IntModel)
    assert int_model.to_data() == 3


def test_create_model_from_kwargs() -> None:
    """Create dict-like models from kwargs."""
    dict_model = create_model_from_kwargs.run(model_cls=Model[dict[str, int]], a=1.23, b='3')

    assert dict_model.to_data() == dict(a=1, b=3)


def test_concat_all_vals_in_datasets_as_args_accepts_positional_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[list[int]]](a=[1], b=[2])
    middle_dataset = Dataset[Model[tuple[str, ...]]](c=['3'])
    right_dataset = Dataset[Model[tuple[int]]](d=(4,))

    output = concat_all_vals_in_datasets_as_args.run(left_dataset, middle_dataset, right_dataset)
    assert is_model_instance(output)
    assert output.full_type() == list[int]
    assert output.to_data() == [1, 2, 3, 4]


def test_concat_all_vals_in_datasets_as_kwargs_accepts_keyword_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[list[int]]](a=[1], b=[2])
    middle_dataset = Dataset[Model[list[int]]](c=[3])
    right_dataset = Dataset[Model[list[int]]](d=[4])

    output = concat_all_vals_in_datasets_as_kwargs.run(
        left=left_dataset,
        middle=middle_dataset,
        right=right_dataset,
    )
    assert is_model_instance(output)
    assert output.full_type() == list[int]
    assert output.to_data() == [1, 2, 3, 4]


def test_union_all_vals_in_datasets_as_kwargs_accepts_keyword_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[dict[str, int]]](a={'a': 1})
    middle_dataset = Dataset[Model[dict[str, int]]](b={'b': 2})
    right_dataset = Dataset[Model[dict[str, int]]](c={'c': 3})

    output = union_all_vals_in_datasets_as_kwargs.run(
        left=left_dataset,
        middle=middle_dataset,
        right=right_dataset,
    )
    assert is_model_instance(output)
    assert output.full_type() == dict[str, int]
    assert output.to_data() == {'a': 1, 'b': 2, 'c': 3}


def test_union_all_vals_in_datasets_as_args_accepts_positional_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[dict[str, int]]](a={'a': 1})
    middle_dataset = Dataset[Model[dict[str, str]]](b={'b': '2'})
    right_dataset = Dataset[Model[dict[str, int]]](c={'c': 3})

    output = union_all_vals_in_datasets_as_args.run(
        left_dataset,
        middle_dataset,
        right_dataset,
    )
    assert is_model_instance(output)
    assert output.full_type() == dict[str, int]
    assert output.to_data() == {'a': 1, 'b': 2, 'c': 3}


def test_union_all_datasets_as_args_accepts_positional_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[dict[str, int]]](left={'a': 1})
    middle_dataset = Dataset[Model[dict[str, int]]](middle={'b': 2})
    right_dataset = Dataset[Model[dict[str, int]]](right={'c': 3})

    output = union_all_datasets_as_args.run(left_dataset, middle_dataset, right_dataset)
    assert isinstance(output, Dataset)
    assert output.get_type() is Model[dict[str, int]]
    assert output.to_data() == {
        'left': {
            'a': 1
        },
        'middle': {
            'b': 2
        },
        'right': {
            'c': 3
        },
    }


def test_union_all_datasets_as_kwargs_accepts_keyword_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[dict[str, int]]](left={'a': 1})
    middle_dataset = Dataset[Model[dict[str, int]]](middle={'b': 2})
    right_dataset = Dataset[Model[dict[str, int]]](right={'c': 3})

    output = union_all_datasets_as_kwargs.run(
        left=left_dataset,
        middle=middle_dataset,
        right=right_dataset,
    )
    assert isinstance(output, Dataset)
    assert output.get_type() is Model[dict[str, int]]
    assert output.to_data() == {
        'left': {
            'a': 1
        },
        'middle': {
            'b': 2
        },
        'right': {
            'c': 3
        },
    }
