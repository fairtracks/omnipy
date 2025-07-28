from typing import Annotated

import pytest

from omnipy.config.data import DataConfig, ModelConfig
from omnipy.data._data_class_creator import DataClassBase, DataClassBaseMeta, DataClassCreator
from omnipy.data.snapshot import SnapshotHolder

from .helpers.mocks import MockDataset, MockModel


def test_init():
    with pytest.raises(TypeError):
        DataClassCreator('something')  # noqa  # pyright: ignore [reportCallIssue]

    data_class_creator_1 = DataClassCreator()
    data_class_creator_2 = DataClassCreator()

    assert data_class_creator_1 != data_class_creator_2


def test_set_config() -> None:
    data_class_creator = DataClassCreator()
    assert data_class_creator.config == DataConfig()

    new_data_config = DataConfig(model=ModelConfig(interactive=False))
    with pytest.raises(AttributeError):
        data_class_creator.config = new_data_config  # type: ignore[misc]

    data_class_creator.set_config(new_data_config)
    assert data_class_creator.config == new_data_config


def test_singular_mock(teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:

    assert isinstance(DataClassBase.data_class_creator, DataClassCreator)

    with pytest.raises(AttributeError):
        DataClassBase.data_class_creator = DataClassCreator()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        MockDataset.data_class_creator = DataClassCreator()  # pyright: ignore

    with pytest.raises(AttributeError):
        MockModel.data_class_creator = DataClassCreator()  # pyright: ignore

    data_class_creator = DataClassBase.data_class_creator
    assert MockDataset.data_class_creator is data_class_creator
    assert MockModel.data_class_creator is data_class_creator

    dataset = MockDataset()
    assert dataset.__class__.data_class_creator is data_class_creator

    model = MockModel()
    assert model.__class__.data_class_creator is data_class_creator

    dataset_new = MockDataset()
    assert dataset_new.__class__.data_class_creator is data_class_creator


def test_deepcopy_context() -> None:
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


def test_config_property_mutable_from_data_class_creator(
        teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:
    _assert_property_is_singularly_mutable(
        property='config',
        property_type=DataConfig,
        set_property_from_data_class=False,
        new_val=DataConfig(model=ModelConfig(interactive=False)),
        property_setter='set_config',
    )


def test_snapshot_holder_property_immutable(
        teardown_reset_data_class_creator: Annotated[None, pytest.fixture]) -> None:
    _assert_property_is_singularly_immutable(
        property='snapshot_holder',
        property_type=SnapshotHolder,
    )


def _assert_property_is_singularly_mutable(property: str,
                                           property_type: type,
                                           set_property_from_data_class: bool,
                                           new_val: object,
                                           property_setter: str | None = None) -> None:
    data_classes = (MockDataset, MockModel, DataClassBase)
    data_objects = (MockDataset(), MockModel())
    initial_val = getattr(DataClassBase.data_class_creator, property)
    assert isinstance(initial_val, property_type)

    _assert_property_in_classes(data_classes, property, initial_val)
    _assert_property_in_objects(data_objects, property, initial_val)

    if set_property_from_data_class:
        assert property_setter is None
        for data_obj in data_objects:
            setattr(data_obj, property, new_val)
    else:
        assert property_setter is not None
        for data_cls in data_classes:
            with pytest.raises(AttributeError):
                set_property_method = getattr(data_cls, property_setter)
                set_property_method(new_val)

            set_property_method = getattr(data_cls.data_class_creator, property_setter)
            set_property_method(new_val)

    _assert_property_in_classes(data_classes, property, new_val)
    _assert_property_in_objects(data_objects, property, new_val)

    new_data_objects = (MockDataset(), MockModel())
    assert new_data_objects[0] is not data_objects[0]
    assert new_data_objects[1] is not data_objects[1]

    _assert_property_in_objects(new_data_objects, property, new_val)


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
