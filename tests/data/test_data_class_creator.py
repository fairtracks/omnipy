from typing import Annotated

import pytest

from data.helpers.mocks import MockDataset, MockModel
from omnipy.api.protocols.public.config import IsDataConfig
from omnipy.config.data import DataConfig
from omnipy.data.data_class_creator import DataClassBase, DataClassBaseMeta, DataClassCreator


def test_data_class_creator_init():
    with pytest.raises(TypeError):
        DataClassCreator('something')  # noqa

    data_class_creator_1 = DataClassCreator()
    data_class_creator_2 = DataClassCreator()

    assert data_class_creator_1 != data_class_creator_2


def test_data_class_creator_set_config() -> None:
    data_class_creator = DataClassCreator()
    assert data_class_creator.config == DataConfig()

    new_data_config = DataConfig(interactive_mode=False)
    with pytest.raises(AttributeError):
        data_class_creator.config = new_data_config

    data_class_creator.set_config(new_data_config)
    assert data_class_creator.config == new_data_config


def test_data_class_creator_singular_mock(
        teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:

    assert isinstance(DataClassBase.data_class_creator, DataClassCreator)

    with pytest.raises(AttributeError):
        DataClassBase.data_class_creator = DataClassCreator()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        MockDataset.data_class_creator = DataClassCreator()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        MockModel.data_class_creator = DataClassCreator()  # type: ignore[misc]

    data_class_creator = DataClassBase.data_class_creator
    assert MockDataset.data_class_creator is data_class_creator
    assert MockModel.data_class_creator is data_class_creator

    dataset = MockDataset()
    assert dataset.__class__.data_class_creator is data_class_creator

    model = MockModel()
    assert model.__class__.data_class_creator is data_class_creator

    dataset_new = MockDataset()
    assert dataset_new.__class__.data_class_creator is data_class_creator


def test_data_class_creator_properties_mock(
        teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:
    data_classes = (MockDataset, MockModel, DataClassBase)
    data_objects = (MockDataset(), MockModel())
    data_config = DataClassBase.data_class_creator.config

    _assert_config_property_in_classes(data_classes, val=data_config)
    _assert_config_property_in_objects(data_objects, val=data_config)

    new_data_config = DataConfig(interactive_mode=False)
    MockDataset.data_class_creator.set_config(new_data_config)

    _assert_config_property_in_classes(data_classes, val=new_data_config)
    _assert_config_property_in_objects(data_objects, val=new_data_config)

    new_data_objects = (MockDataset(), MockModel())
    assert new_data_objects[0] is not data_objects[0]
    assert new_data_objects[1] is not data_objects[1]

    _assert_config_property_in_objects(new_data_objects, val=new_data_config)

    assert not hasattr(MockDataset, 'set_config')
    assert not hasattr(MockModel, 'set_config')
    assert not hasattr(DataClassBase, 'set_config')


def _assert_config_property_in_classes(data_classes: tuple[DataClassBaseMeta, ...],
                                       val: IsDataConfig) -> None:
    for data_cls in data_classes:
        assert getattr(data_cls.data_class_creator, 'config') is val
        assert hasattr(data_cls, 'config')


def _assert_config_property_in_objects(data_objects: tuple[DataClassBase, ...],
                                       val: IsDataConfig) -> None:
    for data_obj in data_objects:
        assert getattr(data_obj.__class__.data_class_creator, 'config') is val
        assert getattr(data_obj, 'config') is val
        assert hasattr(data_obj.__class__, 'config')
