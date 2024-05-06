from omnipy.data.dataset import Dataset, ParamDataset
from omnipy.data.model import Model, ParamModel
from omnipy.modules.general.tasks import convert_dataset


class FloatModel(Model[float]):
    ...


class IntModel(Model[int]):
    ...


class RoundedIntModel(ParamModel[float | int, bool]):
    @classmethod
    def _parse_data(cls, data: float | int, round_to_nearest: bool = False) -> int:
        if isinstance(data, int):
            return data

        return round(data) if round_to_nearest else int(data)

    ...


class FloatDataset(Dataset[FloatModel]):
    ...


class IntDataset(Dataset[IntModel]):
    ...


class RoundedIntDataset(ParamDataset[RoundedIntModel, bool]):
    ...


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


def test_convert_dataset_with_params():
    floats = FloatDataset(a=1.23, b=3.6)
    ints = convert_dataset.run(floats, dataset_cls=RoundedIntDataset, round_to_nearest=True)
    assert isinstance(ints, RoundedIntDataset)
    assert ints.to_data() == dict(a=1, b=4)
