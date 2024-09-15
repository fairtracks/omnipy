from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.param import (bind_adjust_dataset_func,
                               bind_adjust_model_func,
                               params_dataclass,
                               ParamsBase)
from omnipy.modules.general.tasks import convert_dataset


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


RoundedIntModelT = TypeVar('RoundedIntModelT', default=RoundedIntModel)


class _RoundedIntDataset(Dataset[RoundedIntModelT], Generic[RoundedIntModelT]):
    ...


class RoundedIntDataset(_RoundedIntDataset[RoundedIntModel]):
    adjust = bind_adjust_dataset_func(
        _RoundedIntDataset[RoundedIntModel].clone_dataset_cls,
        RoundedIntModel,
        RoundedIntModel.Params,
    )


def test_convert_dataset():
    floats = FloatDataset(a=1.23, b=3.6)
    ints = convert_dataset.run(floats, dataset_cls=IntDataset)
    assert isinstance(ints, IntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_convert_dataset_with_default_params():
    floats = FloatDataset(a=1.23, b=3.6)
    ints = convert_dataset.run(floats, dataset_cls=RoundedIntDataset)
    assert isinstance(ints, RoundedIntDataset)
    assert ints.to_data() == dict(a=1, b=3)


def test_convert_dataset_with_params() -> None:
    RoundToNearestIntDataset = RoundedIntDataset.adjust(
        'RoundToNearestIntDataset', 'RoundToNearestIntModel', round_to_nearest=True)

    floats = FloatDataset(a=1.23, b=3.6)
    ints = convert_dataset.run(floats, dataset_cls=RoundToNearestIntDataset)
    assert isinstance(ints, RoundToNearestIntDataset)
    assert ints.to_data() == dict(a=1, b=4)
