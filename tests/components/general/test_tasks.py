"""Tests for general-purpose dataset and model creation tasks."""

from typing import Generic

from typing_extensions import TypeVar

from omnipy.components.general.tasks import (create_dataset_args,
                                             create_dataset_kwargs,
                                             create_model_args,
                                             create_model_kwargs)
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.param import (bind_adjust_dataset_func,
                               bind_adjust_model_func,
                               params_dataclass,
                               ParamsBase)


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


def test_create_dataset_args():
    """Create datasets from a single positional source dataset."""
    floats = FloatDataset(a=1.23, b=3.6)
    ints = create_dataset_args.run(floats, dataset_cls=IntDataset)
    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_args_with_default_params():
    """Create datasets using default adjustable parameters."""
    floats = FloatDataset(a=1.23, b=3.6)
    ints = create_dataset_args.run(floats, dataset_cls=RoundedIntDataset)
    assert isinstance(ints, RoundedIntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_args_with_params() -> None:
    """Create datasets using customized adjustable parameters."""
    RoundToNearestIntDataset = RoundedIntDataset.adjust(
        'RoundToNearestIntDataset', 'RoundToNearestIntModel', round_to_nearest=True)

    floats = FloatDataset(a=1.23, b=3.6)
    ints = create_dataset_args.run(floats, dataset_cls=RoundToNearestIntDataset)
    assert isinstance(ints, RoundToNearestIntDataset)
    assert ints.to_data() == dict(a=1, b=4)


def test_create_dataset_args_accepts_zero_positional_args() -> None:
    """Create an empty dataset when no positional arguments are provided."""
    ints = create_dataset_args.run(dataset_cls=IntDataset)

    assert isinstance(ints, IntDataset)
    assert ints.to_data() == {}


def test_create_dataset_args_accepts_multiple_positional_pairs() -> None:
    """Create datasets from multiple positional ``(key, value)`` pairs."""
    ints = create_dataset_args.run(('a', 1.23), ('b', 3.6), dataset_cls=IntDataset)

    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_kwargs_from_models() -> None:
    """Create datasets from model instances supplied as kwargs."""
    ints = create_dataset_kwargs.run(
        dataset_cls=RoundedIntDataset,
        a=FloatModel(1.23),
        b=FloatModel(3.6),
    )

    assert isinstance(ints, RoundedIntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_create_dataset_kwargs_from_subdatasets() -> None:
    """Create nested datasets from sub-datasets supplied as kwargs."""
    nested_dataset = create_dataset_kwargs.run(
        dataset_cls=Dataset[Dataset[IntModel]],
        first=FloatDataset(a=1.23),
        second=FloatDataset(b=3.6),
    )

    assert isinstance(nested_dataset['first'], Dataset)
    assert nested_dataset.to_data() == dict(first=dict(a=1), second=dict(b=3))


def test_create_model_args_accepts_multiple_positional_args() -> None:
    """Create models from any number of positional args via tuple-style root input."""
    tuple_model = create_model_args.run(1.23, 3.6, model_cls=Model[tuple[int, ...]])

    assert tuple_model.to_data() == (1, 3)


def test_create_model_args_preserves_single_positional_arg() -> None:
    """Create models from a single positional arg without wrapping it in a tuple."""
    int_model = create_model_args.run(3.6, model_cls=IntModel)

    assert isinstance(int_model, IntModel)
    assert int_model.to_data() == 3


def test_create_model_kwargs() -> None:
    """Create dict-like models from kwargs."""
    dict_model = create_model_kwargs.run(model_cls=Model[dict[str, int]], a=1.23, b='3')

    assert dict_model.to_data() == dict(a=1, b=3)
