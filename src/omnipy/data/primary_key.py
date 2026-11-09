"""Primary-key declarations, deterministic serialization, and Models."""

from collections.abc import Iterable
from types import GenericAlias
from typing import cast, Generic, get_args, get_origin, Literal, TypeVarTuple

from omnipy.data.helpers import TypeVarStore
from omnipy.data.model import Model, ModelMetaclass

_KeyFieldsT = TypeVarTuple('_KeyFieldsT')


class PrimaryKey(Generic[*_KeyFieldsT]):
    """Declare ordered key fields as one or more distinct string Literals.

    ``PrimaryKey[Literal['project'], Literal['sample']]`` declares a composite
    key. Fields remain visible in the records; this type only declares identity.
    """

    def __class_getitem__(cls, params: object) -> GenericAlias:
        field_types = params if isinstance(params, tuple) else (params,)
        field_names: list[str] = []
        if not field_types:
            raise ValueError('Specify one or more primary-key fields')
        for field_type in field_types:
            names = get_args(field_type)
            if get_origin(field_type) is not Literal or len(names) != 1:
                raise TypeError('Each primary-key field must be a single string Literal')
            name = names[0]
            if not isinstance(name, str) or not name:
                raise ValueError('Primary-key field names must be nonempty strings')
            if name in field_names:
                raise ValueError(f'Duplicate primary-key field: {name!r}')
            field_names.append(name)
        return GenericAlias(cls, field_types)


class PrimaryKeyModelMetaclass(ModelMetaclass):
    def __init__(cls, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        cls._primary_key: tuple[str, ...] | None = None

    @property
    def primary_key(cls) -> tuple[str, ...]:
        if cls._primary_key is None:
            type_args = get_args(cast(type[Model], cls).outer_type(with_args=True))
            for type_arg in type_args:
                if get_origin(type_arg) is TypeVarStore:
                    type_arg = get_args(type_arg)[0]
                if get_origin(type_arg) is PrimaryKey:
                    cls._primary_key = tuple(get_args(field)[0] for field in get_args(type_arg))
                    break

        if cls._primary_key is None:
            raise TypeError('Specialize the model with a PrimaryKey declaration')

        return cls._primary_key


def serialize_primary_key(values: Iterable[object]) -> str:
    """Stringify key components, escaping ``%`` and ``|`` for composite keys.

    A component's ``to_data()`` result is used when available. Single-field keys
    are left unescaped. Default address-based object representations are rejected.
    Lists and dictionaries retain Python's string representation and order.
    Collision detection belongs to the collection constructing the keyed data.
    """
    components: list[str] = []
    for value in values:
        to_data = getattr(value, 'to_data', None)
        if callable(to_data):
            value = to_data()
        if type(value).__str__ is object.__str__ and type(value).__repr__ is object.__repr__:
            raise ValueError(
                f'Primary-key values need a stable string representation: {type(value)}'
            )
        components.append(str(value))
    if not components:
        raise ValueError('Specify one or more primary-key values')
    if len(components) == 1:
        return components[0]
    return '|'.join(component.replace('%', '%25').replace('|', '%7C') for component in components)
