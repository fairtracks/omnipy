from typing import get_args, Literal

import pytest

from omnipy.data.model import Model
from omnipy.data.primary_key import (
    PrimaryKey,
    PrimaryKeyModelMetaclass,
    serialize_primary_key,
)


def test_primary_key_preserves_declared_field_order() -> None:
    key = PrimaryKey[Literal['project'], Literal['sample']]
    assert get_args(key) == (Literal['project'], Literal['sample'])


@pytest.mark.parametrize(
    'fields, error',
    [
        ((), ValueError),
        ('id', TypeError),
        (str, TypeError),
        (Literal['a', 'b'], TypeError),
        (Literal[''], ValueError),
        (Literal[1], ValueError),
        ((Literal['id'], Literal['id']), ValueError),
    ],
)
def test_primary_key_rejects_invalid_declarations(fields, error: type[Exception]) -> None:
    with pytest.raises(error):
        PrimaryKey[fields]


@pytest.mark.parametrize(
    'values, expected',
    [
        (('sample',), 'sample'),
        (('a|b%7C',), 'a|b%7C'),
        ((None,), 'None'),
        ((1,), '1'),
        (([1, None],), '[1, None]'),
        (({'b': 2, 'a': 1},), "{'b': 2, 'a': 1}"),
        (('project|north', 'sample%1'), 'project%7Cnorth|sample%251'),
        (('%7C', '|'), '%257C|%7C'),
        (('', None, 1), '|None|1'),
    ],
)
def test_serialize_primary_key(values: tuple[object, ...], expected: str) -> None:
    assert serialize_primary_key(values) == expected


def test_serialize_primary_key_uses_model_data() -> None:
    assert serialize_primary_key((Model[str]('a|b'), Model[int](1))) == 'a%7Cb|1'
    assert serialize_primary_key((Model[list[int]]([1, 2]),)) == '[1, 2]'


def test_serialize_primary_key_rejects_empty_and_unstable_values() -> None:
    with pytest.raises(ValueError, match='one or more'):
        serialize_primary_key(())
    with pytest.raises(ValueError, match='stable string'):
        serialize_primary_key((object(),))


def test_primary_key_metaclass_accepts_declaration_without_type_var_store() -> None:
    class DirectPrimaryKeyModel(
        Model[str | PrimaryKey[Literal['project'], Literal['identity']]],
        metaclass=PrimaryKeyModelMetaclass,
    ): ...

    primary_key = DirectPrimaryKeyModel.primary_key
    assert primary_key == ('project', 'identity')
    assert DirectPrimaryKeyModel.primary_key is primary_key


def test_primary_key_metaclass_requires_primary_key_declaration() -> None:
    class WithoutPrimaryKeyModel(Model[int | str], metaclass=PrimaryKeyModelMetaclass): ...

    with pytest.raises(TypeError, match='Specialize the model with a PrimaryKey declaration'):
        _ = WithoutPrimaryKeyModel.primary_key
