import sys

if sys.version_info >= (3, 11):
    from builtins import ExceptionGroup
else:
    from exceptiongroup import ExceptionGroup

from collections import UserDict
from inspect import ismemberdescriptor
from typing import Annotated, Any, Callable, ClassVar, Generic, Union

from pydantic import BaseConfig, BaseModel, Field, PrivateAttr, ValidationError
from pydantic.class_validators import make_generic_validator
from pydantic.generics import GenericModel
from typing_extensions import Self, TypedDict, TypeVar, TypeVarTuple, Unpack

from omnipy import Model

ModelsT = TypeVarTuple('ModelsT')
ModelsUnionT = TypeVar('ModelsUnionT')
BlueprintHolderT = TypeVar('BlueprintHolderT', bound='BlueprintHolder')
BlueprintT = TypeVar('BlueprintT', bound='Blueprint')


class Blueprint(TypedDict, total=False):
    ...


def make_blueprint_validator(
    blueprint_cls: type[Blueprint],
    config: type[BaseConfig],
    model_classes: tuple[type[Model], ...],
) -> Callable[[Any], dict[str, Any]]:
    from pydantic.annotated_types import create_model_from_typeddict

    BlueprintModel = create_model_from_typeddict(
        blueprint_cls,
        __config__=config,
        __module__=blueprint_cls.__module__,
    )
    blueprint_cls.__pydantic_model__ = BlueprintModel  # type: ignore[attr-defined]
    BlueprintModel.__custom_root_type__

    def blueprint_validator(values: Blueprint) -> dict[str, Any]:
        parsed = {}
        for key, value in values.items():
            exceptions = []
            for model_cls in model_classes:
                try:
                    parsed[key] = model_cls(value)
                    break
                except ValidationError as e:
                    exceptions.append(e)
            else:
                if exceptions:
                    raise ExceptionGroup('Validation errors', exceptions)

        model = BlueprintModel.parse_obj(parsed)
        return {key: getattr(model, key) for key in values.keys() if hasattr(model, key)}

    return blueprint_validator


class BlueprintHolder(GenericModel, UserDict, Generic[BlueprintT, ModelsUnionT]):
    __root__: Annotated[BlueprintT, ModelsUnionT] = Field(default_factory=Blueprint)

    @property
    def data(self) -> BlueprintT:
        print(f'Accessing data: {self.__root__}')
        return self.__root__

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        extra = 'allow'

    @classmethod
    def __init_subclass__(cls, **kwargs):
        print(f'Initializing BlueprintHolder subclass {cls.__name__}')

        super().__init_subclass__(**kwargs)

    def __new__(cls, *args, **kwargs):
        cls.__fields__['__root__'].validators[0] = make_generic_validator(
            make_blueprint_validator(
                cls.__fields__['__root__'].type_,
                cls.__fields__['__root__'].model_config,
                cls.__fields__['__root__'].field_info.extra.get('model_classes'),
            ))
        return super().__new__(cls, *args, **kwargs)

    def __setitem__(self, key: str, value: Any):
        print(f'Setting item {key} to {value}')
        self.__root__[key] = value
        print('Triggering validation...')
        self.__root__ = self.__root__

    def __delitem__(self, key: str):
        print(f'Deleting item {key}')
        del self.__root__[key]
        print('Triggering validation...')
        self.__root__ = self.__root__


#         self._blueprint_holder.__root__ = self._blueprint_holder.__root__
#         self._dataset.files = self._blueprint_holder


class Dataset(BaseModel, UserDict, Generic[Unpack[ModelsT]]):
    _model_classes: ClassVar[tuple[type[Model], ...]] = PrivateAttr()
    _blueprint_cls: ClassVar[type[Blueprint]] = PrivateAttr()

    files: BlueprintHolder = Field(default_factory=BlueprintHolder)

    @property
    def data(self) -> BlueprintHolder:
        print(f'Accessing files: {self.files}')
        return self.files

    @classmethod
    def blueprint_annotations(cls) -> dict[str, Any]:
        if cls._blueprint_cls:
            return cls._blueprint_cls.__annotations__
        else:
            return {}

    def __init_subclass__(cls, blueprint: type[Blueprint] = Blueprint, **kwargs):
        print(f'Initializing subclass {cls.__name__} with blueprint={blueprint}')
        print(f'cls: {cls}, type(blueprint): {type(blueprint)}')
        super().__init_subclass__(**kwargs)
        if blueprint != cls._blueprint_cls:
            cls._set_blueprint_cls(blueprint, cls._model_classes)

    def __class_getitem__(cls, params: tuple[type[Model], ...]) -> Self:
        created_cls = super().__class_getitem__(params)
        if not isinstance(params, tuple):
            params = (params,)

        cls._model_classes = params
        if ismemberdescriptor(cls._blueprint_cls):
            cls._blueprint_cls = Blueprint

        created_cls._set_blueprint_cls(cls._blueprint_cls, cls._model_classes)
        return created_cls

    @classmethod
    def _set_blueprint_cls(
        cls,
        blueprint_cls: type[Blueprint],
        model_classes: tuple[type[Model], ...],
    ) -> None:
        blueprint_holder_cls = BlueprintHolder[
            blueprint_cls,  # type: ignore[valid-type]
            Union[model_classes]  # type: ignore[valid-type]
        ]
        blueprint_holder_cls.__fields__['__root__'].field_info.extra[
            'model_classes'] = model_classes
        cls.__fields__['files'].type_ = blueprint_holder_cls
        cls.__fields__['files'].default_factory = blueprint_holder_cls

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True


#
# dd = Dataset[Model[int], Model[str]]()
# dd['einar'] = 32
# dd['ingrid'] = 42
# omnipy_hurra = Dataset[
#     Model[int],
# ]()
# dd['sveinung'] = 'asd'
#
#
# class MyBlueprint(Blueprint, total=False):
#     pappa: Model[str]
#
#
# class MyDataset(Dataset[Model[int]], blueprint=MyBlueprint):
#     ...
#
#
# asd = MyDataset()
# asd['a'] = '23'
