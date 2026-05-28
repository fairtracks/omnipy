from dataclasses import dataclass
from typing import Callable

from omnipy.data.model import Model

from ..helpers.classes import FloatDictHolder, FloatHolder, MyFloatObject
from ..helpers.datasets import MyFloatObjDataset
from ..helpers.models import MyFloatObjModel, PydanticChildModel


@dataclass(frozen=True)
class ModelValueAssignmentSpec:
    value_factory: Callable[[], object]
    setitem_target_factory: Callable[[], Model]
    setattr_target_factory: Callable[[], Model]
    expected_value: object
    forbidden_key: str | None = None


def case_omnipy_model() -> ModelValueAssignmentSpec:
    return ModelValueAssignmentSpec(
        value_factory=lambda: MyFloatObjModel(MyFloatObject(int_part=4, float_part=0.5)),
        setitem_target_factory=lambda: Model[dict[str, float]]({}),
        setattr_target_factory=lambda: Model[FloatHolder](),
        expected_value=4.5,
    )


def case_dataset() -> ModelValueAssignmentSpec:
    return ModelValueAssignmentSpec(
        value_factory=lambda: MyFloatObjDataset(pi=MyFloatObject(int_part=3, float_part=0.5)),
        setitem_target_factory=lambda: Model[dict[str, dict[str, float]]]({}),
        setattr_target_factory=lambda: Model[FloatDictHolder](),
        expected_value={'pi': 3.5},
    )


def case_pydantic_model() -> ModelValueAssignmentSpec:
    return ModelValueAssignmentSpec(
        value_factory=lambda: PydanticChildModel(**{
            '@id': 7, 'value': 1.5
        }),
        setitem_target_factory=lambda: Model[dict[str, dict[str, float]]]({}),
        setattr_target_factory=lambda: Model[FloatDictHolder](),
        expected_value={
            '@id': 7.0, 'value': 1.5
        },
        forbidden_key='id',
    )
