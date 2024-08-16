from typing import Annotated

import pytest

from data.helpers.mocks import MockDataset, MockModel
from omnipy.api.protocols.public.config import IsDataConfig
from omnipy.config.data import DataConfig
from omnipy.data.data_class_creator import DataClassBase, DataClassBaseMeta, DataClassCreator
from omnipy.util.helpers import SnapshotHolder


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


def test_data_class_creator_deepcopy_context() -> None:
    creator = DataClassCreator()

    top_level_entry_func_calls = []
    top_level_exit_func_calls = []

    def top_lvl_entry_func():
        top_level_entry_func_calls.append(True)

    def top_lvl_exit_func():
        top_level_exit_func_calls.append(True)

    with creator.deepcopy_context(top_lvl_entry_func, top_lvl_exit_func) as first_level:
        assert first_level == 1
        assert len(top_level_entry_func_calls) == 1
        assert len(top_level_exit_func_calls) == 0

        with creator.deepcopy_context(top_lvl_entry_func, top_lvl_exit_func) as second_level:
            assert second_level == 2
            assert len(top_level_entry_func_calls) == 1
            assert len(top_level_exit_func_calls) == 0

        assert len(top_level_entry_func_calls) == 1
        assert len(top_level_exit_func_calls) == 0

    assert len(top_level_entry_func_calls) == 1
    assert len(top_level_exit_func_calls) == 1

    try:
        with creator.deepcopy_context(top_lvl_entry_func, top_lvl_exit_func) as first_level:
            assert first_level == 1
            assert len(top_level_entry_func_calls) == 2
            assert len(top_level_exit_func_calls) == 1

            with creator.deepcopy_context(top_lvl_entry_func, top_lvl_exit_func) as second_level:
                assert second_level == 2
                assert len(top_level_entry_func_calls) == 2
                assert len(top_level_exit_func_calls) == 1

                raise RuntimeError('Something is wrong')

    except RuntimeError:
        assert len(top_level_entry_func_calls) == 2
        assert len(top_level_exit_func_calls) == 2


def test_data_class_creator_config_property_mock(
        teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:
    _assert_property_is_singularly_mutable(
        property='config',
        property_setter='set_config',
        property_type=DataConfig,
        new_val=DataConfig(interactive_mode=False),
    )


def test_data_class_creator_snapshot_holder_property_mock(
        teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:
    _assert_property_is_singularly_immutable(
        property='snapshot_holder',
        property_type=SnapshotHolder,
    )


def _assert_property_is_singularly_mutable(property: str,
                                           property_setter: str,
                                           property_type: type,
                                           new_val: object):
    data_classes = (MockDataset, MockModel, DataClassBase)
    data_objects = (MockDataset(), MockModel())
    initial_val = getattr(DataClassBase.data_class_creator, property)
    assert isinstance(initial_val, property_type)

    _assert_property_in_classes(data_classes, property, initial_val)
    _assert_property_in_objects(data_objects, property, initial_val)

    set_property_method = getattr(MockDataset.data_class_creator, property_setter)
    set_property_method(new_val)

    _assert_property_in_classes(data_classes, property, new_val)
    _assert_property_in_objects(data_objects, property, new_val)

    new_data_objects = (MockDataset(), MockModel())
    assert new_data_objects[0] is not data_objects[0]
    assert new_data_objects[1] is not data_objects[1]

    _assert_property_in_objects(new_data_objects, property, new_val)

    assert not hasattr(MockDataset, property_setter)
    assert not hasattr(MockModel, property_setter)
    assert not hasattr(DataClassBase, property_setter)


def _assert_property_is_singularly_immutable(property: str, property_type: type):
    data_classes = (MockDataset, MockModel, DataClassBase)
    data_objects = (MockDataset(), MockModel())
    initial_val = getattr(DataClassBase.data_class_creator, property)
    assert isinstance(initial_val, property_type)

    _assert_property_in_classes(data_classes, property, initial_val)
    _assert_property_in_objects(data_objects, property, initial_val)

    property_setter = f'set_{property}'
    assert not hasattr(MockDataset, property_setter)
    assert not hasattr(MockModel, property_setter)
    assert not hasattr(DataClassBase, property_setter)
    assert not hasattr(MockDataset.data_class_creator, property_setter)


def _assert_property_in_classes(data_classes: tuple[DataClassBaseMeta, ...],
                                property: str,
                                val: object) -> None:
    for data_cls in data_classes:
        assert getattr(data_cls.data_class_creator, property) is val
        assert hasattr(data_cls, property)


def _assert_property_in_objects(data_objects: tuple[DataClassBase, ...], property: str,
                                val: object) -> None:
    for data_obj in data_objects:
        assert getattr(data_obj.__class__.data_class_creator, property) is val
        assert getattr(data_obj, property) is val
        assert hasattr(data_obj.__class__, property)
