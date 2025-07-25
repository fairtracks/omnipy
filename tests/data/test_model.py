from collections.abc import Callable, Sequence
from copy import copy, deepcopy
from dataclasses import dataclass
from datetime import datetime
import gc
from math import floor
import os
from textwrap import dedent
from types import MappingProxyType, MethodType, NotImplementedType, UnionType
from typing import (Annotated,
                    Any,
                    cast,
                    ForwardRef,
                    Generic,
                    get_args,
                    List,
                    Literal,
                    Optional,
                    Type,
                    TypeAlias,
                    Union)

import pytest
import pytest_cases as pc
from typing_extensions import TypeVar

from omnipy.data.helpers import TypeVarStore
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsModel
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util._pydantic import ValidationError
import omnipy.util._pydantic as pyd
from omnipy.util.setdeque import SetDeque

from ..helpers.functions import assert_model, assert_val
from ..helpers.protocols import AssertModelOrValFunc
from .helpers.classes import MyFloatObject, MyList, MyNumberBase, MyPath
from .helpers.models import (CBA,
                             DefaultStrModel,
                             LiteralFiveModel,
                             LiteralFiveOrTextModel,
                             LiteralTextModel,
                             MyFloatObjModel,
                             MyFwdRefModel,
                             MyNestedFwdRefModel,
                             MyPydanticModel,
                             NumberModel,
                             ParamUpperStrModel,
                             PydanticChildModel,
                             PydanticParentModel,
                             UppercaseModel,
                             WordSplitterModel)

T = TypeVar('T', default=object)
U = TypeVar('U', default=object)


def test_no_model() -> None:
    # Correctly instantiating a model in the beginning of the test implicitly tests whether
    # creating a model sets the field-related class members of Model, such that a later object
    # instantiation without a specified model reuses the previous fields. This which would have
    # happened if `_depopulate_root_field()` were not called in `Model.__class_getitem__()`.
    Model[int]()

    with pytest.raises(TypeError):
        Model()

    with pytest.raises(TypeError):

        class ModelSubclass(Model):
            ...

        ModelSubclass()


def test_init_and_data() -> None:
    model = Model[int]()
    assert (isinstance(model, Model))
    assert (model.__class__.__name__ == 'Model[int]')

    class StrModel(Model[str]):
        ...

    str_model = StrModel()
    assert (isinstance(str_model, StrModel))
    assert (isinstance(str_model, Model))
    assert (str_model.__class__.__name__ == StrModel.__name__)

    assert Model[int]().to_data() == 0
    assert Model[str]().to_data() == ''
    assert Model[dict]().to_data() == {}
    assert Model[list]().to_data() == []

    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[list]([2, 4, 'b', {}]).to_data() == [2, 4, 'b', {}]
    assert Model[dict]({'a': 2, 'b': True}).to_data() == {'a': 2, 'b': True}
    assert Model[dict](a=2, b=True).to_data() == {'a': 2, 'b': True}
    assert Model[dict]((('a', 2), ('b', True))).to_data() == {'a': 2, 'b': True}


def test_init_model_as_input() -> None:
    assert Model[int](Model[float](4.5)).to_data() == 4
    assert Model[tuple[int, ...]](Model[list[float]]([4.5, 2.3])).to_data() == (4, 2)

    assert Model[Model[int]](Model[float](4.5)).content == Model[int](4)
    assert Model[Model[int]](Model[float](4.5)).to_data() == 4


def test_init_converting_model_as_input() -> None:
    assert MyFloatObjModel().content == MyFloatObject()
    my_float_model = MyFloatObjModel()
    my_float_model.from_data(4.5)
    assert my_float_model.content == MyFloatObject(int_part=4, float_part=0.5)
    assert my_float_model.to_data() == 4.5

    assert Model[float](my_float_model).content == 4.5
    assert MyFloatObjModel(Model[float](4.5)).to_data() == 4.5


def test_error_init() -> None:
    with pytest.raises(TypeError):
        assert Model[tuple[int, ...]](12, 2, 4).to_data() == 12  # type: ignore
    assert Model[tuple[int, ...]]((12, 2, 4)).to_data() == (12, 2, 4)

    with pytest.raises(AssertionError):
        Model[int](123, __root__=234)

    with pytest.raises(AssertionError):
        Model[int](123, other=234)

    with pytest.raises(AssertionError):
        Model[int](__root__=123, other=234)


def test_class_init_forwardref(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    class MyForwardRefNoNameModel(Model[ForwardRef]):
        ...

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyForwardRefNoNameModel()

    class MyForwardRefModel(Model[ForwardRef('SomeClass')]):  # type: ignore[misc]
        ...

    class MyForwardRefStrModel(Model['SomeClass']):
        ...

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyForwardRefModel()

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyForwardRefStrModel()

    class SomeClass:
        ...

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyForwardRefModel()

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyForwardRefStrModel()

    MyForwardRefModel.update_forward_refs(SomeClass=SomeClass)
    MyForwardRefModel()

    MyForwardRefStrModel.update_forward_refs(SomeClass=SomeClass)
    MyForwardRefStrModel()


def test_class_init_generic_with_forwardref(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    class MyGenericModel(Model[T], Generic[T]):
        ...

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyGenericModel[ForwardRef('SomeClass')]()  # type: ignore[misc, operator]

    with pytest.raises(TypeError, match='Cannot instantiate model'):
        MyGenericModel['SomeClass']()

    class SomeClass:
        ...

    MyGenericModel[ForwardRef('SomeClass')].update_forward_refs(  # type: ignore[misc]
        SomeClass=SomeClass)
    MyGenericModel[ForwardRef('SomeClass')]()  # type: ignore[misc, operator]

    MyGenericModel['SomeClass'].update_forward_refs(SomeClass=SomeClass)
    MyGenericModel['SomeClass']()


def test_class_init_recursive_model_through_generic_hack_with_forwardref(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(RuntimeError):

        class MyRecursiveModel(Model[list['MyRecursiveModel']]):
            ...

    with pytest.raises(RuntimeError):

        class MyNewRecursiveModel(Model[list['MyOtherRecursiveModel'] | None]):
            ...

        class MyOtherRecursiveModel(Model[MyNewRecursiveModel]):
            ...

    with pytest.raises(RuntimeError):

        class MyNewerRecursiveModel(Model[list['MyNewerForwardRefAlias'] | None]):
            ...

        MyNewerForwardRefAlias: TypeAlias = MyNewerRecursiveModel  # noqa: F841

    class MyGenericListModel(Model[list[T | None]], Generic[T]):
        ...

    class MyNewestForwardRefModel(MyGenericListModel['MyNewestForwardRefAlias']):
        ...

    MyNewestForwardRefAlias: TypeAlias = MyNewestForwardRefModel

    with pytest.raises(pyd.ConfigError):
        MyNewestForwardRefModel([MyNewestForwardRefModel([MyNewestForwardRefModel()])])
    MyNewestForwardRefModel.update_forward_refs(MyNewestForwardRefAlias=MyNewestForwardRefAlias)

    MyNewestForwardRefModel([MyNewestForwardRefModel([MyNewestForwardRefModel()])])


def test_load() -> None:
    model = Model[int]()
    model.from_data(12)
    assert model.to_data() == 12

    model.from_data(123)
    assert model.to_data() == 123

    assert Model[int](-234).to_data() == -234

    assert Model[int](__root__=-1).to_data() == -1  # for pydantic internals

    with pytest.raises(RuntimeError):
        Model[int](5).__root__ = 12  # noqa

    with pytest.raises(RuntimeError):
        Model[int](5).foo = True  # noqa


def test_get_inner_outer_type() -> None:
    int_model = Model[int]()
    assert int_model.outer_type() == int
    assert int_model.inner_type() == int
    assert int_model.is_nested_type() is False

    list_of_ints_model = Model[list[int]]()
    assert list_of_ints_model.outer_type() == list
    assert list_of_ints_model.outer_type(with_args=True) == list[int]
    assert list_of_ints_model.inner_type() == int
    assert list_of_ints_model.inner_type(with_args=True) == int
    assert list_of_ints_model.is_nested_type() is True

    list_of_lists_of_ints_model = Model[list[list[int]]]()
    assert list_of_lists_of_ints_model.outer_type() == list
    assert list_of_lists_of_ints_model.outer_type(with_args=True) == list[list[int]]
    assert list_of_lists_of_ints_model.inner_type() == list
    assert list_of_lists_of_ints_model.inner_type(with_args=True) == list[int]
    assert list_of_lists_of_ints_model.is_nested_type() is True

    dict_of_strings_to_list_of_ints_model = Model[dict[str, list[int]]]()
    assert dict_of_strings_to_list_of_ints_model.outer_type() == dict
    assert dict_of_strings_to_list_of_ints_model.outer_type(with_args=True) == dict[str, list[int]]
    assert dict_of_strings_to_list_of_ints_model.inner_type() == list
    assert dict_of_strings_to_list_of_ints_model.inner_type(with_args=True) == list[int]
    assert dict_of_strings_to_list_of_ints_model.is_nested_type() is True

    tuple_of_different_types_model = Model[tuple[int, str, float]]()
    assert tuple_of_different_types_model.outer_type() == tuple
    assert tuple_of_different_types_model.outer_type(with_args=True) == tuple[int, str, float]
    assert tuple_of_different_types_model.inner_type() == tuple
    assert tuple_of_different_types_model.inner_type(with_args=True) == tuple[int, str, float]
    assert tuple_of_different_types_model.is_nested_type() is False

    union_of_different_types_model = Model[int | str | float]()
    assert union_of_different_types_model.outer_type() == UnionType
    assert union_of_different_types_model.outer_type(with_args=True) == int | str | float
    assert union_of_different_types_model.inner_type() == UnionType
    assert union_of_different_types_model.inner_type(with_args=True) == int | str | float
    assert union_of_different_types_model.is_nested_type() is False

    outer_optional_model = Model[dict[str, list[int]] | None]()
    assert outer_optional_model.outer_type() == UnionType
    assert outer_optional_model.outer_type(with_args=True) == dict[str, list[int]] | None
    assert outer_optional_model.inner_type() == UnionType
    assert outer_optional_model.inner_type(with_args=True) == dict[str, list[int]] | None
    assert outer_optional_model.is_nested_type() is False

    inner_optional_model = Model[dict[str, Optional[list[int]]]]()
    assert inner_optional_model.outer_type() == dict
    assert inner_optional_model.outer_type(with_args=True) == dict[str, list[int] | None]
    assert inner_optional_model.inner_type() == UnionType
    assert inner_optional_model.inner_type(with_args=True) == list[int] | None
    assert inner_optional_model.is_nested_type() is True


def test_equality_other_models() -> None:
    assert Model[int]() == Model[int]()

    model = Model[int]()
    model.from_data(123)
    assert model == Model[int](123)
    assert model != Model[int](234)

    # Equality is dependent on the datatype/model, in contrast to pydantic.
    # Relevant issue: https://github.com/pydantic/pydantic/pull/3066
    assert Model[int](1) != Model[pyd.PositiveInt](1)

    assert Model[list[int]]([1, 2, 3]) == Model[list[int]]([1.0, 2.0, 3.0])
    assert Model[list[int]]([1, 2, 3]) != Model[list[float]]([1.0, 2.0, 3.0])
    assert Model[list[int]]([1, 2, 3]) != Model[list[int]]([1, 2])
    assert Model[list[int]]([1, 2, 3]) != Model[list[int | float]]([1, 2, 3])
    assert Model[list[int]]([1, 2, 3]) != Model[List[int]]([1, 2, 3])


def test_complex_equality() -> None:
    model_1 = Model[list[int]]()
    model_1.content = [1, 2, 3]
    model_2 = Model[list[int]]()
    model_2.content = (1, 2, 3)  # type: ignore[assignment]

    assert model_1 != model_2
    model_2.validate_content()
    assert model_1 == model_2


# TODO: Revisit with pydantic v2. Expected to change
def test_equality_with_pydantic_not_symmetric() -> None:
    class RootPydanticInt(pyd.BaseModel):
        __root__: int

    class MyInt(Model[int]):
        ...

    assert RootPydanticInt(__root__=1) != 1
    assert RootPydanticInt(__root__=1) == {'__root__': 1}
    assert MyInt(1) != 1
    assert MyInt(1) != {'__root__': 1}

    assert RootPydanticInt(__root__=1) == MyInt(1)
    assert MyInt(1) != RootPydanticInt(__root__=1)


def test_equality_with_pydantic_as_args() -> None:
    class PydanticModel(pyd.BaseModel):
        a: int = 0

    class OtherPydanticModel(pyd.BaseModel):
        a: float = 0

    assert PydanticModel(a=1) == OtherPydanticModel(a=1)

    class MyModel(Model[PydanticModel]):
        ...

    class MyOtherModel(Model[OtherPydanticModel]):
        ...

    assert MyModel(a=1) == MyModel(a=1)
    assert MyModel(a=1) == MyModel({'a': 1})
    assert MyModel(a=1) != MyModel(a=2)
    assert MyModel(a=1) != MyOtherModel(a=1)

    class EqualPydanticModel(PydanticModel):
        ...

    class MyEqualModel(Model[EqualPydanticModel]):
        ...

    assert MyModel(a=1) != MyEqualModel(a=1)

    class MyInherited(MyModel):
        ...

    assert MyModel(a=1) != MyInherited(a=1)


def test_name_qualname_and_module() -> None:
    assert Model.__name__ == 'Model'
    assert Model.__qualname__ == 'Model'
    assert Model.__module__ == 'omnipy.data.model'

    assert Model[int].__name__ == 'Model[int]'
    assert Model[int].__qualname__ == 'Model[int]'
    assert Model[int].__module__ == 'omnipy.data.model'

    assert Model[Model[None]].__name__ == 'Model[Model[None]]'
    assert Model[Model[None]].__qualname__ == 'Model[Model[None]]'
    assert Model[Model[None]].__module__ == 'omnipy.data.model'

    assert Model[dict[str, Model[None]]].__name__ == 'Model[dict[str, Model[None]]]'
    assert Model[dict[str, Model[None]]].__qualname__ == 'Model[dict[str, Model[None]]]'
    assert Model[dict[str, Model[None]]].__module__ == 'omnipy.data.model'

    assert Model[list[T]][int].__name__ == 'Model[list[~T]][int]'
    assert Model[list[T]][int].__qualname__ == 'Model[list[~T]][int]'
    assert Model[list[T]][int].__module__ == 'omnipy.data.model'

    ABC_PREFIX = 'test_name_qualname_and_module.<locals>.ABC.'
    DEF_PREFIX = 'test_name_qualname_and_module.<locals>.DEF.'

    class ABC:
        class MyModel(Model[list[T]], Generic[T]):
            ...

        assert MyModel.__name__ == 'MyModel'
        assert MyModel.__qualname__ == ABC_PREFIX + 'MyModel'

        assert MyModel[int].__name__ == 'MyModel[int]'
        assert MyModel[int].__qualname__ == ABC_PREFIX + 'MyModel[int]'

        assert MyModel[U].__name__ == 'MyModel[~U]'
        assert MyModel[U].__qualname__ == ABC_PREFIX + 'MyModel[~U]'

        assert MyModel.__module__ == 'tests.data.test_model'

    class DEF:
        class MyTupleModel(ABC.MyModel[tuple[T, U]], Generic[T, U]):
            ...

        assert MyTupleModel.__name__ == 'MyTupleModel'
        assert MyTupleModel.__qualname__ == DEF_PREFIX + 'MyTupleModel'

        assert MyTupleModel[int, str].__name__ == 'MyTupleModel[int, str]'
        assert MyTupleModel[int, str].__qualname__ == DEF_PREFIX + 'MyTupleModel[int, str]'

        assert MyTupleModel.__module__ == 'tests.data.test_model'

    assert ABC.MyModel[int].__name__ == 'MyModel[int]'
    assert ABC.MyModel[int].__qualname__ == ABC_PREFIX + 'MyModel[int]'

    assert ABC.MyModel[ABC.MyModel[int]].__name__ == 'MyModel[MyModel[int]]'
    assert ABC.MyModel[ABC.MyModel[int]].__qualname__ == ABC_PREFIX + 'MyModel[MyModel[int]]'

    assert ABC.MyModel[Union[str, ABC.MyModel[str | int]]].__name__ == \
           'MyModel[str | MyModel[str | int]]'
    assert ABC.MyModel[Union[str, ABC.MyModel[str | int]]].__qualname__ == \
           ABC_PREFIX + 'MyModel[str | MyModel[str | int]]'

    assert ABC.MyModel[ABC.MyModel[Union[str, int]] | str].__name__ == \
           'MyModel[MyModel[str | int] | str]'
    assert ABC.MyModel[ABC.MyModel[str | int] | str].__qualname__ == \
           ABC_PREFIX + 'MyModel[MyModel[str | int] | str]'

    assert DEF.MyTupleModel[int, str].__name__ == 'MyTupleModel[int, str]'
    assert DEF.MyTupleModel[int, str].__qualname__ == DEF_PREFIX + 'MyTupleModel[int, str]'

    assert DEF.MyTupleModel[int, ABC.MyModel[str]].__name__ == \
           'MyTupleModel[int, MyModel[str]]'
    assert DEF.MyTupleModel[int, ABC.MyModel[str]].__qualname__ == \
           (DEF_PREFIX + 'MyTupleModel[int, MyModel[str]]')

    assert MyFwdRefModel.__name__ == 'MyGenericModel[NumberModel]'
    assert MyFwdRefModel.__qualname__ == 'CBA.MyGenericModel[NumberModel]'
    assert MyFwdRefModel.__module__ == 'tests.data.helpers.models'

    assert MyNestedFwdRefModel.__name__ == 'MyGenericModel[str | NumberModel]'
    assert MyNestedFwdRefModel.__qualname__ == 'CBA.MyGenericModel[str | NumberModel]'
    assert MyNestedFwdRefModel.__module__ == 'tests.data.helpers.models'

    assert (CBA.MyGenericModel[ForwardRef('ABC.MyModel[int]')].__name__ ==  # noqa: W504
            'MyGenericModel[ABC.MyModel[int]]')
    assert (CBA.MyGenericModel[ForwardRef('ABC.MyModel[int]')].__qualname__ ==  # noqa: W504
            'CBA.MyGenericModel[ABC.MyModel[int]]')
    assert (CBA.MyGenericModel[ForwardRef('ABC.MyModel[int]')].__module__ ==  # noqa: W504
            'tests.data.helpers.models')

    assert (CBA.MyGenericModel['Union[str, ABC.MyModel[int]]'].__name__ ==  # noqa: W504
            'MyGenericModel[Union[str, ABC.MyModel[int]]]')
    assert (CBA.MyGenericModel['Union[str, ABC.MyModel[int]]'].__qualname__ ==  # noqa: W504
            'CBA.MyGenericModel[Union[str, ABC.MyModel[int]]]')
    assert (CBA.MyGenericModel['Union[str, ABC.MyModel[int]]'].__module__ ==  # noqa: W504
            'tests.data.helpers.models')


# TODO: Revisit test_name_qualname_reuse_typevar_known_issue with pydantic v2. Expected to change
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue due to bug in pydantic v1 where a generic model defined with some TypeVar(s)
parametrized with the exact same TypeVar(s) are assumed to be the same model:

    https://github.com/pydantic/pydantic/blob/5ebcdc13b83fba5da34ad9b0f008f7b4faf89396/pydantic/generics.py#L110

This causes issues if generic models inherit from each other while having the same TypeVar(s).
TypeVar(s) in Python are bound only within the scope of a class or function, so the same TypeVar(s)
in different classes should not be assumed to be the same.

For now, the only consequence of the bug that we are aware of is that the `__name__` and
`__qualname__` of the models are slightly incorrect and will not print the TypeVars. However,
worse consequences might be hidden in the code.
""")
def test_name_qualname_reuse_typevar_known_issue() -> None:
    class MyModel(Model[T], Generic[T]):
        ...

    assert MyModel[T].__name__ == 'MyModel[~T]'
    assert MyModel[T].__qualname__ == 'MyModel[~T]'


def test_repr() -> None:
    assert repr(Model[int]) == "<class 'omnipy.data.model.Model[int]'>"
    assert repr(Model[int](5)) == 'Model[int](5)'

    assert repr(Model[Model[int]]) \
           == "<class 'omnipy.data.model.Model[Model[int]]'>"
    assert repr(Model[Model[int]](Model[int](5))) == 'Model[Model[int]](Model[int](5))'

    assert repr(MyFwdRefModel) == \
           "<class 'tests.data.helpers.models.CBA.MyGenericModel[NumberModel]'>"
    assert repr(MyFwdRefModel(NumberModel(5))) == \
           'MyGenericModel[NumberModel](NumberModel(5))'

    assert repr(MyNestedFwdRefModel) == \
           "<class 'tests.data.helpers.models.CBA.MyGenericModel[str | NumberModel]'>"
    assert repr(MyNestedFwdRefModel('abc')) == \
           "MyGenericModel[str | NumberModel]('abc')"


def test_repr_pretty() -> None:
    from IPython.lib.pretty import pretty

    model = Model[list[int]]([123])
    assert pretty([model]) == '[Model[list[int]]([123])]'


def _issubclass_and_isinstance(model_cls_a: Type[Model], model_cls_b: Type[Model]) -> bool:
    is_subclass = issubclass(model_cls_a, model_cls_b)

    model_a = model_cls_a()
    is_instance = isinstance(model_a, model_cls_b)

    return is_subclass and is_instance


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason='To be implemented later. Should be issubtype instead')
def test_issubclass_and_isinstance() -> None:
    assert _issubclass_and_isinstance(Model[str], Model[str])
    assert not _issubclass_and_isinstance(Model[int], Model[str])

    assert _issubclass_and_isinstance(Model[int], Model[int | str])
    assert _issubclass_and_isinstance(Model[str], Model[int | str])

    assert _issubclass_and_isinstance(Model[list[str]], Model[list])

    class MyStrList(Model[list[str]]):
        ...

    assert _issubclass_and_isinstance(MyStrList, Model[list])


@pc.parametrize(
    'copy_func',
    [lambda model: model.copy(), lambda model: model.copy(deep=False), copy],
    ids=['model.copy()', 'model.copy(deep=False)', 'copy.copy()'],
)
def test_copy(copy_func: Callable[[Model], Model]) -> None:
    model = Model[list[list[int]]]([[123], [456]])

    model_copy = copy_func(model)

    assert model_copy is not model
    assert model_copy == model

    assert model_copy.content is not model.content
    assert model_copy.content == model.content

    assert model_copy.content[0] is model.content[0]
    assert model_copy.content[1] is model.content[1]

    assert not model_copy.has_snapshot()

    assert model_copy.__fields_set__ == {'__root__'}


@pc.parametrize(
    'deepcopy_func',
    [lambda model: model.copy(deep=True), deepcopy],
    ids=['model.copy(deep=True)', 'copy.deepcopy()'],
)
def test_deepcopy(deepcopy_func: Callable[[Model], Model]) -> None:
    model = Model[list[list[int]]]([[123], [456]])

    model_deepcopy = deepcopy_func(model)

    assert model_deepcopy is not model
    assert model_deepcopy == model

    assert model_deepcopy.content is not model.content
    assert model_deepcopy.content == model.content

    assert model_deepcopy.content[0] is not model.content[0]
    assert model_deepcopy.content[0] == model.content[0]
    assert model_deepcopy.content[1] is not model.content[1]
    assert model_deepcopy.content[1] == model.content[1]

    assert not model_deepcopy.has_snapshot()

    assert model_deepcopy.__fields_set__ == {'__root__'}


def test_parse_convertible_data() -> None:
    NumberModel = Model[int]

    model_1 = NumberModel(123.3)
    assert model_1.to_data() == 123

    model_2 = NumberModel()
    model_2.from_data(123.9)
    assert model_2.to_data() == 123

    model_3 = NumberModel('-123')
    assert model_3.to_data() == -123

    model_4 = NumberModel(True)
    assert model_4.to_data() == 1

    assert model_1 == model_2
    assert model_1 != model_3
    assert model_2 != model_4
    assert model_3 != model_4


def test_parse_convertible_sequences() -> None:
    model = Model[list[int]](range(5))
    assert model.to_data() == [0, 1, 2, 3, 4]

    model = Model[tuple[str, ...]](range(5))  # type: ignore[assignment]
    assert model.to_data() == ('0', '1', '2', '3', '4')

    with pytest.raises(ValidationError):
        Model[list[str]]('abcde')

    with pytest.raises(ValidationError):
        Model[list[str]](b'abcde')


def test_load_inconvertible_data() -> None:
    class NumberModel(Model[int]):
        ...

    model = NumberModel()

    with pytest.raises(ValidationError):
        model.from_data('fifteen')
    assert model.content == 0

    with pytest.raises(ValidationError):
        NumberModel([])
    assert model.content == 0


def test_load_inconvertible_data_strict_type() -> None:
    class StrictNumberModel(Model[pyd.StrictInt]):
        ...

    model = StrictNumberModel()

    with pytest.raises(ValidationError):
        model.from_data(123.4)
    assert model.content == 0

    with pytest.raises(ValidationError):
        model.from_data('234')
    assert model.content == 0

    with pytest.raises(ValidationError):
        StrictNumberModel(234.9)
    assert model.content == 0

    model.from_data(123)
    assert model.content == 123


def test_load_inconvertible_data_nested_type() -> None:
    class ListOfIntsModel(Model[list[int]]):
        ...

    model = ListOfIntsModel()

    with pytest.raises(ValidationError):
        model.from_data(123.4)
    assert model.content == []

    model.from_data([])
    assert model.content == []

    with pytest.raises(ValidationError):
        model.from_data(['abc'])
    assert model.content == []

    with pytest.raises(ValidationError):
        ListOfIntsModel([[]])
    assert model.content == []

    model.from_data([123, 234])
    assert model.content == [123, 234]


def test_error_invalid_model() -> None:

    with pytest.raises(TypeError):

        class DoubleTypesModel(Model[int, str]):  # type: ignore[type-arg]
            ...


def test_tuple_of_anything() -> None:
    class TupleModel(Model[tuple]):
        ...

    assert TupleModel().to_data() == ()
    assert TupleModel((1, 's', True)).to_data() == (1, 's', True)
    with pytest.raises(ValidationError):
        TupleModel(1)


def test_tuple_of_single_type() -> None:
    class TupleModel(Model[tuple[int]]):
        ...

    assert TupleModel().to_data() == (0,)
    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 2, 3))

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_tuple_of_single_type_repeated() -> None:
    class TupleModel(Model[tuple[int, ...]]):
        ...

    assert TupleModel().to_data() == ()
    assert TupleModel((1, 2, 3)).to_data() == (1, 2, 3)
    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_fixed_tuple_of_different_types() -> None:
    class TupleModel(Model[tuple[int, str]]):
        ...

    assert TupleModel().to_data() == (0, '')
    assert TupleModel((123, 'abc')).to_data() == (123, 'abc')
    assert TupleModel(('123', 123)).to_data() == (123, '123')

    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 2, 3))

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_basic_union() -> None:
    # Note: Python 3.10 introduced a shorthand form for Union[TypeA, TypeB]:
    #
    #   TypeA | TypeB
    #
    # The requirements for omnipy is Python 3.10, and there have been some hashin issues with mostly
    # the older form of this notation, so the newer should be preferred. The old form are kept
    # several places in this file tests related to the notation.

    class UnionModel(Model[int | str | list]):
        ...

    assert UnionModel(15).to_data() == 15
    assert UnionModel('abc').to_data() == 'abc'
    assert UnionModel([]).to_data() == []


# TODO: Revisit test_nested_annotated_union_default_not_defined_by_first_type_known_issue with
#       new Python versions
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue due to a caching problem in the `typing` package in python, which causes a bug in
pydantic (https://github.com/pydantic/pydantic/issues/4519). The first initiation of a nested
type from the typing package is cached by the typing package and defines the order of the second
initiation (even though the order of int and str is the opposite). Works when split into
individual tests. New Union nomenclature introduced in Python 3.10 does not help when nested
under Annotated. Issue is not present in e.g. List or Dict as the default values of these are
[] and {}, respectively.
""")
def test_nested_annotated_union_default_not_defined_by_first_type_known_issue() -> None:
    class IntFirstAnnotatedUnionModel(Model[Annotated[Union[int, str], 'test']]):
        ...

    assert IntFirstAnnotatedUnionModel().to_data() == 0

    class StrFirstAnnotatedUnionModel(Model[Annotated[Union[str, int], 'test']]):
        ...

    assert StrFirstAnnotatedUnionModel().to_data() == ''

    class IntFirstAnnotatedUnionModelNew(Model[Annotated[int | str, 'test']]):
        ...

    assert IntFirstAnnotatedUnionModelNew().to_data() == 0

    class StrFirstAnnotatedUnionModelNew(Model[Annotated[str | int, 'test']]):
        ...

    assert StrFirstAnnotatedUnionModelNew().to_data() == ''


def test_nested_annotated_union_default_not_defined_by_first_type() -> None:
    class IntFirstUnionModel(Model[Union[int, str]]):
        ...

    assert IntFirstUnionModel().to_data() == 0

    class StrFirstUnionModel(Model[Union[str, int]]):
        ...

    assert StrFirstUnionModel().to_data() == ''

    class IntFirstNewUnionModel(Model[int | str]):
        ...

    assert IntFirstNewUnionModel().to_data() == 0

    class StrFirstNewUnionModel(Model[str | int]):
        ...

    assert StrFirstNewUnionModel().to_data() == ''


def test_union_default_value_from_first_callable_type() -> None:
    class FirstTypeNotInstantiatableUnionModel(Model[Any | str]):
        ...

    assert FirstTypeNotInstantiatableUnionModel().to_data() == ''

    class NoTypeInstantiatableUnionModel(Model[Any | Type]):
        ...

    with pytest.raises(TypeError):
        NoTypeInstantiatableUnionModel()


def test_union_default_value_if_any_none() -> None:
    class NoneFirstUnionModel(Model[None | str]):
        ...

    assert NoneFirstUnionModel().to_data() is None

    class NoneSecondUnionModel(Model[str | None]):
        ...

    assert NoneSecondUnionModel().to_data() is None


def test_parsing_independent_on_union_type_order() -> None:
    class FloatIntUnionModel(Model[Union[float, int]]):
        ...

    assert FloatIntUnionModel(2.0).to_data() == 2.0
    assert type(FloatIntUnionModel(2.0).to_data()) == float

    assert FloatIntUnionModel(15).to_data() == 15
    assert type(FloatIntUnionModel(15).to_data()) == int

    assert FloatIntUnionModel('2.0').to_data() == 2.0
    assert type(FloatIntUnionModel('2.0').to_data()) == float

    assert FloatIntUnionModel('15').to_data() == 15.0
    assert type(FloatIntUnionModel('15').to_data()) == float

    class IntFloatUnionModel(Model[Union[int, float]]):
        ...

    assert IntFloatUnionModel(2.0).to_data() == 2.0
    assert type(IntFloatUnionModel(2.0).to_data()) == float

    assert IntFloatUnionModel(15).to_data() == 15
    assert type(IntFloatUnionModel(15).to_data()) == int

    assert IntFloatUnionModel('2.0').to_data() == 2.0
    assert type(IntFloatUnionModel('2.0').to_data()) == float

    assert IntFloatUnionModel('15').to_data() == 15
    assert type(IntFloatUnionModel('15').to_data()) == int

    class FloatIntStrUnionModel(Model[Union[float, int, str]]):
        ...

    assert FloatIntStrUnionModel(2.0).to_data() == 2.0
    assert type(FloatIntStrUnionModel(2.0).to_data()) == float

    assert FloatIntStrUnionModel(15).to_data() == 15
    assert type(FloatIntStrUnionModel(15).to_data()) == int

    assert FloatIntStrUnionModel('2.0').to_data() == '2.0'
    assert type(FloatIntStrUnionModel('2.0').to_data()) == str

    assert FloatIntStrUnionModel('15').to_data() == '15'
    assert type(FloatIntStrUnionModel('15').to_data()) == str


def test_optional() -> None:
    class OptionalIntModel(Model[Optional[int]]):
        ...

    assert OptionalIntModel().to_data() is None
    assert OptionalIntModel(None).to_data() is None
    assert OptionalIntModel(13).to_data() == 13
    assert OptionalIntModel('12').to_data() == 12

    with pytest.raises(ValidationError):
        OptionalIntModel([None])

    with pytest.raises(ValidationError):
        OptionalIntModel('None')


def test_nested_union_default_value() -> None:
    class NestedUnion(Model[Union[Union[str, int], float]]):
        ...

    assert NestedUnion().to_data() == ''

    class NestedUnionWithOptional(Model[Union[Union[Optional[str], int], float]]):
        ...

    assert NestedUnionWithOptional().to_data() is None

    class NestedUnionWithSingleTypeTuple(Model[Union[Union[tuple[str], int], float]]):
        ...

    assert NestedUnionWithSingleTypeTuple().to_data() == ('',)


def test_nested_annotated_default_value() -> None:
    class MyIntModel(Model[Annotated[int, 'This is my cool integer model']]):
        ...

    assert MyIntModel().to_data() == 0

    class MyIntListModel(Model[Annotated[list[int], 'This is my awesome integer list model']]):
        ...

    assert MyIntListModel().to_data() == []


def test_none_allowed() -> None:
    class NoneModel(Model[None]):
        ...

    assert NoneModel().to_data() is None
    assert NoneModel(None).to_data() is None

    with pytest.raises(ValidationError):
        NoneModel(13)

    with pytest.raises(ValidationError):
        NoneModel('None')

    class MaybeNumberModelOptional(Model[Optional[int]]):
        ...

    class MaybeNumberModelUnion(Model[Union[int, None]]):
        ...

    class MaybeNumberModelUnionNew(Model[int | None]):
        ...

    class MaybeNumberModelSubclass(MaybeNumberModelUnionNew):
        ...

    class MaybeNumberWrapperModel(Model[MaybeNumberModelUnionNew]):
        ...

    for model_cls in [
            MaybeNumberModelOptional,
            MaybeNumberModelUnion,
            MaybeNumberModelUnionNew,
            MaybeNumberModelSubclass,
            MaybeNumberWrapperModel,
    ]:
        assert model_cls().to_data() is None
        assert model_cls(None).to_data() is None
        assert model_cls(13).to_data() == 13

        with pytest.raises(ValidationError):
            model_cls('None')


def test_none_not_allowed() -> None:
    class IntListModel(Model[list[int]]):
        ...

    class IntDictModel(Model[dict[int, int]]):
        ...

    class IntOrFloatModel(Model[int | float]):
        ...

    for model_cls in [IntListModel, IntDictModel, IntOrFloatModel]:
        assert cast(Model, model_cls()).to_data() is not None

        with pytest.raises(ValidationError):
            model_cls(None)


@pc.fixture(scope='function')
@pc.parametrize(
    'none_variant, none_variant_target_content',
    (
        (None, None),
        (Model[None], Model[None](None)),
        (int | None, None),
        (list[int] | None, None),
        (Model[None] | int, Model[None](None)),
        (Model[None] | dict[int, int], Model[None](None)),
        (Model[int | None], Model[int | None](None)),
        (Model[list[int] | None], Model[list[int] | None](None)),
    ),
    ids=[
        'None',
        'Model[None]',
        'int | None',
        'list[int] | None',
        'Model[None] | int',
        'Model[None] | dict[int, int]',
        'Model[int | None]',
        'Model[list[int] | None]',
    ],
)
def none_variant_and_target_content(
    none_variant: None | type[Model],
    none_variant_target_content: None | Model,
) -> tuple[None | type[Model], None | Model]:
    return none_variant, none_variant_target_content


def test_list_of_none_variants(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class ListOfNoneVariantModel(Model[list[none_variant]]):  # type: ignore[valid-type]
        ...

    assert ListOfNoneVariantModel().content == []
    assert ListOfNoneVariantModel([]).content == []

    with pytest.raises(ValidationError):
        ListOfNoneVariantModel(None)

    assert ListOfNoneVariantModel((None,)).content == [none_variant_target_content]
    assert ListOfNoneVariantModel([None]).content == [none_variant_target_content]

    with pytest.raises(ValidationError):
        ListOfNoneVariantModel({1: None})


def test_variable_tuple_of_none_variants(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class VariableTupleOfNoneModel(Model[tuple[none_variant, ...]]):  # type: ignore[valid-type]
        ...

    assert VariableTupleOfNoneModel().content == ()
    assert VariableTupleOfNoneModel(()).content == ()

    with pytest.raises(ValidationError):
        VariableTupleOfNoneModel(None)

    assert VariableTupleOfNoneModel((None,)).content == (none_variant_target_content,)
    assert VariableTupleOfNoneModel([None]).content == (none_variant_target_content,)

    with pytest.raises(ValidationError):
        VariableTupleOfNoneModel({1: None})


def test_fixed_tuple_of_none_variants(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class FixedTupleOfNoneModel(Model[tuple[none_variant,
                                            none_variant]]):  # type: ignore[valid-type]
        ...

    target_content = (none_variant_target_content, none_variant_target_content)

    assert FixedTupleOfNoneModel().content == target_content

    with pytest.raises(ValidationError):
        assert FixedTupleOfNoneModel(())

    with pytest.raises(ValidationError):
        FixedTupleOfNoneModel(None)

    with pytest.raises(ValidationError):
        FixedTupleOfNoneModel((None,))

    with pytest.raises(ValidationError):
        FixedTupleOfNoneModel([None])

    assert FixedTupleOfNoneModel((None, None)).content == target_content
    assert FixedTupleOfNoneModel([None, None]).content == target_content

    with pytest.raises(ValidationError):
        FixedTupleOfNoneModel([None, 'None'])

    with pytest.raises(ValidationError):
        FixedTupleOfNoneModel({1: None})


def test_dict_of_none_variants_as_val(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class DictOfInt2NoneModel(Model[dict[int, none_variant]]):  # type: ignore[valid-type]
        ...

    assert DictOfInt2NoneModel().content == {}
    assert DictOfInt2NoneModel({}).content == {}

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel([None])

    assert DictOfInt2NoneModel({1: None}).content == {1: none_variant_target_content}
    assert DictOfInt2NoneModel(MappingProxyType({1: None})).content == {
        1: none_variant_target_content
    }

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel({None: 1})

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel({'hello': None})


def test_dict_of_none_variants_as_key(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class DictOfNone2IntModel(Model[dict[none_variant, int]]):  # type: ignore[valid-type]
        ...

    assert DictOfNone2IntModel().content == {}
    assert DictOfNone2IntModel({}).content == {}

    with pytest.raises(ValidationError):
        DictOfNone2IntModel(None)

    with pytest.raises(ValidationError):
        DictOfNone2IntModel([None])

    assert DictOfNone2IntModel({None: 1}).content == {none_variant_target_content: 1}
    assert DictOfNone2IntModel(MappingProxyType({None: 1})).content == {
        none_variant_target_content: 1
    }

    with pytest.raises(ValidationError):
        DictOfNone2IntModel({1: None})

    with pytest.raises(ValidationError):
        DictOfNone2IntModel({None: 'hello'})


def test_dict_of_none_variants_as_val_and_key(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class DictOfNone2NoneModel(Model[dict[none_variant, none_variant]]):  # type: ignore[valid-type]
        ...

    assert DictOfNone2NoneModel().content == {}
    assert DictOfNone2NoneModel({}).content == {}

    with pytest.raises(ValidationError):
        DictOfNone2NoneModel(None)

    with pytest.raises(ValidationError):
        DictOfNone2NoneModel([None])

    assert DictOfNone2NoneModel({
        None: None
    }).content == {
        none_variant_target_content: none_variant_target_content
    }
    assert DictOfNone2NoneModel(MappingProxyType({None: None})).content == {
        none_variant_target_content: none_variant_target_content
    }

    with pytest.raises(ValidationError):
        DictOfNone2NoneModel({'hello': None})

    with pytest.raises(ValidationError):
        DictOfNone2NoneModel({None: 'hello'})


def test_union_of_none_variants(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class UnionOfNoneModel(Model[none_variant | int]):  # type: ignore[valid-type]
        ...

    assert UnionOfNoneModel().content == none_variant_target_content

    assert UnionOfNoneModel(None).content == none_variant_target_content

    with pytest.raises(ValidationError):
        UnionOfNoneModel((None,))

    with pytest.raises(ValidationError):
        UnionOfNoneModel([None])

    with pytest.raises(ValidationError):
        UnionOfNoneModel([None, None])

    assert UnionOfNoneModel(123).content == 123

    with pytest.raises(ValidationError):
        UnionOfNoneModel('None')

    with pytest.raises(ValidationError):
        UnionOfNoneModel({1: None})


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason=dedent("""
        Current pydantic v1 None hack do not support deeply nested lists or dicts (when the
        level of nesting is 2 or more"""),
)
def test_doubly_nested_list_and_dict_of_none_variants_known_issue(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    class ListOfListOfNoneVariant(Model[list[list[none_variant]]]):  # type: ignore[valid-type]
        ...

    assert ListOfListOfNoneVariant() == ListOfListOfNoneVariant([])
    assert ListOfListOfNoneVariant([]) == ListOfListOfNoneVariant([])

    with pytest.raises(ValidationError):
        ListOfListOfNoneVariant(None)

    with pytest.raises(ValidationError):
        ListOfListOfNoneVariant([None])

    assert ListOfListOfNoneVariant([[None]
                                    ]) == ListOfListOfNoneVariant([[none_variant_target_content]])

    with pytest.raises(ValidationError):
        ListOfListOfNoneVariant([{1: None}])

    class DictOfInt2DictOfInt2NoneVariant(Model[dict[
            int,
            dict[
                int,
                none_variant_target_content,  # type: ignore[valid-type]
            ]]]):
        ...

    DictOfInt2DictOfInt2NoneVariant()

    with pytest.raises(ValidationError):
        DictOfInt2DictOfInt2NoneVariant(None)

    with pytest.raises(ValidationError):
        DictOfInt2DictOfInt2NoneVariant([None])

    with pytest.raises(ValidationError):
        DictOfInt2DictOfInt2NoneVariant({1: None})

    assert DictOfInt2DictOfInt2NoneVariant({1: {2: None}}) == \
        DictOfInt2DictOfInt2NoneVariant({1: {2: none_variant_target_content}})

    with pytest.raises(ValidationError):
        DictOfInt2DictOfInt2NoneVariant({1: {'hello': None}})


# Simpler working test added to illustrate more complex fails related to pydantic issue:
# https://github.com/pydantic/pydantic/issues/3836
def test_nested_model_classes_none_as_default() -> None:
    class MaybeNumberModelOptional(Model[Optional[int]]):
        ...

    class MaybeNumberModelUnion(Model[Union[int, None]]):
        ...

    class MaybeNumberModelUnionNew(Model[int | None]):
        ...

    class OuterMaybeNumberModelOptional(Model[MaybeNumberModelOptional]):
        ...

    class OuterMaybeNumberModelUnion(Model[MaybeNumberModelUnion]):
        ...

    class OuterMaybeNumberModelUnionNew(Model[MaybeNumberModelUnionNew]):
        ...

    assert OuterMaybeNumberModelOptional().content == MaybeNumberModelOptional(None)

    assert OuterMaybeNumberModelUnion().content == MaybeNumberModelUnion(None)

    assert OuterMaybeNumberModelUnionNew().content == MaybeNumberModelUnionNew(None)


# Simpler working test added to illustrate more complex fails related to pydantic issue:
# https://github.com/pydantic/pydantic/issues/3836


def test_nested_model_classes_inner_generic_none_as_default(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    BaseT = TypeVar('BaseT')

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class OuterMaybeNumberModel(BaseModel[none_variant]):
        ...

    assert OuterMaybeNumberModel().content == none_variant_target_content


def test_union_nested_model_classes_inner_optional_generic_none_as_default() -> None:
    class MaybeNumberModel(Model[Optional[int]]):
        ...

    class MaybeStringModel(Model[Optional[str]]):
        ...

    BaseT = TypeVar('BaseT', default=Union[MaybeNumberModel, MaybeStringModel])

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class OuterMaybeNumberModel(BaseModel[Union[MaybeNumberModel, MaybeStringModel]]):
        ...

    assert OuterMaybeNumberModel().content == MaybeNumberModel(None)


def test_union_nested_model_classes_inner_forwardref_generic_list_of_none(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant, none_variant_target_content = none_variant_and_target_content

    BaseT = TypeVar('BaseT')

    class GenericListModel(Model[list[BaseT]], Generic[BaseT]):
        ...

    class ListModel(GenericListModel['FullModel']):
        ...

    FullModel: TypeAlias = Union[none_variant, ListModel]

    ListModel.update_forward_refs(FullModel=FullModel)

    assert ListModel().content == []
    assert ListModel([None]).content == [none_variant_target_content]
    assert ListModel([[None]]).content == [ListModel([none_variant_target_content])]

    with pytest.raises(ValidationError):
        ListModel(None)


def test_union_nested_model_classes_inner_forwardref_double_generic_none_as_default(
    none_variant_and_target_content: Annotated[tuple[None | type[Model], None | Model], pc.fixture],
) -> None:
    none_variant = none_variant_and_target_content[0]

    BaseT = TypeVar('BaseT', default=None)

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class NoneVariantModel(BaseModel[none_variant]):
        ...

    class GenericListModel(BaseModel[list[BaseT]], Generic[BaseT]):
        ...

    class ListModel(GenericListModel['FullModel']):
        ...

    FullModel: TypeAlias = ListModel | NoneVariantModel

    ListModel.update_forward_refs(FullModel=FullModel)

    assert ListModel().content == []


def test_recursive_list_model_with_none() -> None:
    class MyMaybeNumbersModel(Model[None | int]):
        ...

    class MyGenericListModel(Model[list[T]], Generic[T]):
        ...

    class MyListModel(MyGenericListModel['MyMaybeNumberOrListAlias']):
        ...

    MyMaybeNumberOrListAlias: TypeAlias = MyMaybeNumbersModel | MyListModel

    MyListModel.update_forward_refs(MyMaybeNumberOrListAlias=MyMaybeNumberOrListAlias)

    with pytest.raises(ValidationError):
        MyListModel(None)

    assert MyListModel([None]).content == [MyMaybeNumbersModel(None)]

    assert MyListModel([[None, 3], None]).content == [
        MyListModel([MyMaybeNumbersModel(None), MyMaybeNumbersModel(3)]), MyMaybeNumbersModel(None)
    ]


# TODO: Revisit test_recursive_dict_model_with_none with new Python versions supporting PEP695 and
#       pydantic v2


def test_recursive_generic_tuple_model_with_none() -> None:
    class MyGenericScalarModel(Model[T], Generic[T]):
        ...

    class MyGenericOnlyTuplesAndScalarsModel(
            Model[tuple[TypeVarStore[T]
                        | ForwardRef('MyGenericOnlyTuplesAndScalarsAlias'), ...]],
            Generic[T]):
        ...

    MyGenericOnlyTuplesAndScalarsAlias: TypeAlias = \
        MyGenericScalarModel[T] | MyGenericOnlyTuplesAndScalarsModel[T]

    MyGenericOnlyTuplesAndScalarsModel.update_forward_refs(
        MyGenericOnlyTuplesAndScalarsAlias=MyGenericOnlyTuplesAndScalarsAlias)

    class MyOnlyTuplesAndIntsModel(Model[MyGenericOnlyTuplesAndScalarsModel[int]]):
        ...

    with pytest.raises(ValidationError):
        MyOnlyTuplesAndIntsModel(None)

    with pytest.raises(ValidationError):
        MyOnlyTuplesAndIntsModel([None])

    with pytest.raises(ValidationError):
        MyOnlyTuplesAndIntsModel([[1, None], 2])

    assert MyOnlyTuplesAndIntsModel([[1, 2], 3]).content == \
        MyGenericOnlyTuplesAndScalarsModel[int](
            (MyGenericOnlyTuplesAndScalarsModel[int](
                (MyGenericScalarModel[int](1),
                 MyGenericScalarModel[int](2))),
             MyGenericScalarModel[int](3)))

    class MyOnlyTuplesAndNoneModel(Model[MyGenericOnlyTuplesAndScalarsModel[None]]):
        ...

    with pytest.raises(ValidationError):
        MyOnlyTuplesAndNoneModel(None)

    assert MyOnlyTuplesAndNoneModel([None]).content == \
        MyGenericOnlyTuplesAndScalarsModel[None]((MyGenericScalarModel[None](None),))

    assert MyOnlyTuplesAndNoneModel([[None, None], None]).content == \
        MyGenericOnlyTuplesAndScalarsModel[None](
            (MyGenericOnlyTuplesAndScalarsModel[None](
                (MyGenericScalarModel[None](None),
                 MyGenericScalarModel[None](None))),
             MyGenericScalarModel[None](None)))


def test_import_export_methods() -> None:
    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[dict]({'a': 2}).to_data() == {'a': 2}
    assert Model[list]([2, 4, 'b']).to_data() == [2, 4, 'b']

    assert Model[int](12).content == 12
    assert Model[str]('test').content == 'test'
    assert Model[dict]({'a': 2}).content == {'a': 2}
    assert Model[list]([2, 4, 'b']).content == [2, 4, 'b']

    assert Model[int](12).to_json() == '12'
    assert Model[str]('test').to_json() == '"test"'
    assert Model[dict]({'a': 2}).to_json(pretty=False) == '{"a": 2}'
    assert Model[list]([2, 4, 'b']).to_json(pretty=False) == '[2, 4, "b"]'

    model_int = Model[int]()
    model_int.from_json('12')
    assert model_int.to_data() == 12

    model_int.content = '13'  # type: ignore[assignment]
    assert model_int.content == '13'
    model_int.validate_content()
    assert model_int.content == 13
    assert model_int.to_data() == 13

    model_int.from_data(14)
    assert model_int.content == 14
    model_int.from_data('14')
    assert model_int.content == 14

    model_str = Model[str]()
    model_str.from_json('"test"')
    assert model_str.content == 'test'
    assert model_str.to_data() == 'test'
    model_str.from_data('test')
    assert model_str.content == 'test'
    assert model_str.to_data() == 'test'

    model_str.content = 13  # type: ignore[assignment]
    assert model_str.content == 13
    model_str.validate_content()
    assert model_str.content == '13'
    assert model_str.to_data() == '13'

    model_dict = Model[dict]()
    model_dict.from_json('{"a": 2}')
    assert model_dict.content == {'a': 2}
    assert model_dict.to_data() == {'a': 2}

    model_dict.content = {'b': 3}
    assert model_dict.content == {'b': 3}
    assert model_dict.to_data() == {'b': 3}

    model_list = Model[list]()
    model_list.from_json('[2, 4, "b"]')
    assert model_list.to_data() == [2, 4, 'b']

    model_list.content = [True, 'text', -47.9]
    assert model_list.content == [True, 'text', -47.9]
    assert model_list.to_data() == [True, 'text', -47.9]

    std_description = Model._get_standard_field_description()
    assert Model[int].to_json_schema() == dedent('''\
    {
      "title": "Model[int]",
      "description": "''' + std_description + '''",
      "type": "integer"
    }''')  # noqa: Q001

    assert Model[str].to_json_schema() == dedent('''\
    {
      "title": "Model[str]",
      "description": "''' + std_description + '''",
      "type": "string"
    }''')  # noqa: Q001

    assert Model[dict].to_json_schema() == dedent('''\
    {
      "title": "Model[dict]",
      "description": "''' + std_description + '''",
      "type": "object"
    }''')  # noqa: Q001

    assert Model[list].to_json_schema() == dedent('''\
    {
      "title": "Model[list]",
      "description": "''' + std_description + '''",
      "type": "array",
      "items": {}
    }''')  # noqa: Q001


# This would probably cause more trouble than it's worth and is (possibly permanently) put on ice
# def test_mimic_isinstance() -> None:
#     assert isinstance(Model[int](), int)
#     assert not isinstance(Model[int](), str)
#     assert isinstance(Model[str](), str)
#     assert isinstance(Model[str](), int)
#
#     assert isinstance(Model[list](), Sequence)
#     assert not isinstance(Model[list](), Mapping)
#     assert isinstance(Model[dict[str, str]](), Mapping)
#     assert isinstance(Model[dict[str, str]](), Sequence)
#
#     class MyParentClass:
#         ...
#
#     class MyChildClass(MyParentClass):
#         ...
#
#     assert not isinstance(Model[int](), MyParentClass)
#     assert not isinstance(Model[int](), MyChildClass)
#
#     assert isinstance(Model[MyParentClass](), MyParentClass)
#     assert isinstance(Model[MyChildClass](), MyChildClass)
#
#     assert not isinstance(Model[MyParentClass](), MyChildClass)
#     assert isinstance(Model[MyChildClass](), MyParentClass)
#
#
# def test_mimic_isinstance_union() -> None:
#     assert not isinstance(Model[int | str](), UnionType)
#     assert not isinstance(Model[int | str](1), UnionType)
#     assert not isinstance(Model[int | str]('1'), UnionType)
#
#     assert not isinstance(Model[int | str](), int)
#     assert isinstance(Model[int | str](1), int)
#     assert not isinstance(Model[int | str]('1'), int)
#
#     assert not isinstance(Model[int | str](), str)
#     assert isinstance(Model[int | str](1), str)
#     assert not isinstance(Model[int | str]('1'), str)


def test_model_of_pydantic_model_with_model_of_pydantic_model_children(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    invalid_child_model = Model[PydanticChildModel]({'@id': 12, 'value': 2})
    invalid_child_model.value = '2.22'
    # Model is validated as top-level 'value' attribute is set
    assert invalid_child_model.content.value == 2.22

    invalid_child_model.content.value = '2.22'
    # So we set the value to a string directly in the content to set up the test
    assert invalid_child_model.content.value == '2.22'

    # The __init__() of the child model, Model[PydanticChildModel], detects that the input value is
    # another omnipy Model and revalidates it
    model = MyPydanticModel[list[Model[PydanticChildModel]]]({
        '@id': '1', 'children': [
            {
                '@id': '10', 'value': 1.23
            },
            invalid_child_model,
        ]
    })

    assert model.content.id == 1
    assert len(model.content.children) == 2
    assert model.content.children[0].id == 10
    assert model.content.children[1].value == 2.22

    model.id = '2'
    # Model is validated as top-level 'id' attribute is set
    assert model.content.id == 2

    # When the child pydantic model is wrapped as an omnipy Model, it is also validated when value
    # is set
    model.children[0].value = '2.46'
    assert model.content.children[0].value == 2.46

    with pytest.raises(ValidationError):
        model.children[0].id = 'abc'

    if not runtime.config.data.model.interactive:
        # Manual reset of invalid change above
        model.content.children[0].id = 10
    assert model.children[0].id == 10

    model.children[0].id = 11
    assert model.to_data() == {
        '@id': 2, 'children': [
            {
                '@id': 11, 'value': 2.46
            },
            {
                '@id': 12, 'value': 2.22
            },
        ]
    }


def test_model_of_pydantic_model_with_pydantic_model_children(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    invalid_child_model = PydanticChildModel(**{'@id': 12, 'value': 2})
    invalid_child_model.value = '2.22'

    model_1 = MyPydanticModel[list[PydanticChildModel]]({
        '@id': '1', 'children': [
            {
                '@id': '10', 'value': 1.23
            },
            invalid_child_model,
        ]
    })

    # Unlike an omnipy-wrapped pydantic model, the __init__() of a standard pydantic model does not
    # revalidate other pydantic models provided as input. Also, the top-level omnipy Model does not
    # detect that the input contains a nested pydantic model and does not revalidate it.
    assert model_1.content.children[1].value == '2.22'

    # Validation can, however, be manually triggered by validate_content()
    model_1.validate_content()
    assert model_1.content.children[1].value == 2.22

    # Another workaround is to manually provide a pydantic model as input at the top lever, which
    # will trigger revalidation of any  nested pydantic models
    model_2 = MyPydanticModel[list[PydanticChildModel]](
        PydanticParentModel(**{
            '@id': '1', 'children': [
                {
                    '@id': '10', 'value': 1.23
                },
                invalid_child_model,
            ]
        }))

    assert model_2.content.id == 1
    assert len(model_2.content.children) == 2
    assert model_2.content.children[1].value == 2.22
    assert model_2.content.children[0].id == 10

    model_2.id = '2'
    # Model is validated as top-level 'id' attribute is set
    assert model_2.content.id == 2

    model_2.children[0].value = '2.46'
    # Model is not validated as child attributes are set (as Model does not know about the changes)
    assert model_2.content.children[0].value == '2.46'
    # Model is instead validated as 'children' attribute is accessed
    assert model_2.children[0].value == 2.46

    model_2.children[0].id = 'abc'
    # As validation is postponed, so is the raising of validation error, here as 'children'
    # attribute is accessed
    with pytest.raises(ValidationError):
        model_2.children

    if not runtime.config.data.model.interactive:
        # Manual reset of invalid change above
        model_2.content.children[0].id = 10
    assert model_2.children[0].id == 10

    model_2.children[0].id = 11
    assert model_2.to_data() == {
        '@id': 2, 'children': [
            {
                '@id': 11, 'value': 2.46
            },
            {
                '@id': 12, 'value': 2.22
            },
        ]
    }


def _assert_no_snapshot(model: Model[T]):
    assert model.has_snapshot() is False
    with pytest.raises(AssertionError):
        assert model.snapshot
    with pytest.raises(AssertionError):
        model.content_validated_according_to_snapshot()


def test_weakly_referenced_snapshot_after_validation(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    Model.data_class_creator.snapshot_holder.clear()
    assert len(Model.data_class_creator.snapshot_holder._deepcopy_memo) == 0

    model = Model[list[int]]([123])
    snapshot_holder = model.snapshot_holder

    _assert_no_snapshot(model)
    assert len(model.snapshot_holder) == 0

    model.validate_content()

    if runtime.config.data.model.interactive:
        assert len(snapshot_holder) == 1
        assert model.has_snapshot() is True
        assert model.snapshot == model.content
        assert model.snapshot is not model.content
    else:
        assert len(snapshot_holder) == 0
        _assert_no_snapshot(model)

    del model

    assert len(snapshot_holder) == 0


def test_weakly_referenced_snapshot_deepcopy_memo_entry(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    snapshot_holder = model.snapshot_holder
    deepcopy_memo = snapshot_holder._deepcopy_memo

    assert len(deepcopy_memo) == 0

    model.validate_content()

    if runtime.config.data.model.interactive:
        assert len(deepcopy_memo) == 1
        entry_memo_key = tuple(deepcopy_memo.keys())[0]
        assert deepcopy_memo[entry_memo_key] == model.content
        assert deepcopy_memo[entry_memo_key] is not model.content
        assert deepcopy_memo[entry_memo_key] == model.snapshot
        assert deepcopy_memo[entry_memo_key] is model.snapshot
    else:
        assert len(deepcopy_memo) == 0

    del model

    assert len(deepcopy_memo) == (1 if runtime.config.data.model.interactive else 0)
    snapshot_holder.delete_scheduled_deepcopy_content_ids()
    assert len(snapshot_holder) == 0


@dataclass
class ModelCase:
    new_model_func: Callable[[], Model]
    deepcopy_memo_count: int
    content_modify_func: Callable[..., None]
    target_content: Any


@pc.fixture(scope='function')
@pc.parametrize(
    'case',
    [
        ModelCase(
            new_model_func=lambda: Model[list[int]]([123]),
            deepcopy_memo_count=1,
            content_modify_func=lambda content: content.append(234),
            target_content=[123, 234],
        ),
        ModelCase(
            new_model_func=lambda: Model[MyList](MyList(123)),
            deepcopy_memo_count=3,
            content_modify_func=lambda content: content.__iadd__(MyList(234)),
            target_content=MyList(123, 234),
        ),
    ],
    ids=['Model[list[int]]', 'Model[MyList]'],
)
def model_case(case: ModelCase,) -> ModelCase:
    return case


def test_snapshot_deleted_with_new_content(
    runtime: Annotated[IsRuntime, pytest.fixture],
    model_case: Annotated[ModelCase, pc.fixture],
) -> None:
    model = model_case.new_model_func()

    model.validate_content()

    assert len(model.snapshot_holder) == (1 if runtime.config.data.model.interactive else 0)

    if runtime.config.data.model.interactive:
        old_snapshot_id = id(model.snapshot)
        old_content_id = id(model.content)

    model_case.content_modify_func(model.content)
    model.validate_content()

    assert len(model.snapshot_holder) == (1 if runtime.config.data.model.interactive else 0)

    if runtime.config.data.model.interactive:
        assert id(model.snapshot) != old_snapshot_id
        assert id(model.content) != old_content_id

    assert model.content == model_case.target_content


def test_snapshot_deepcopy_memo_entry_deleted_with_new_content(
    runtime: Annotated[IsRuntime, pytest.fixture],
    model_case: Annotated[ModelCase, pc.fixture],
) -> None:
    model = model_case.new_model_func()

    deepcopy_memo = model.snapshot_holder._deepcopy_memo
    deepcopy_memo.clear()
    model.snapshot_holder.clear()

    model.validate_content()

    assert len(deepcopy_memo) == (
        model_case.deepcopy_memo_count if runtime.config.data.model.interactive else 0)

    if runtime.config.data.model.interactive:
        old_entry_memo_key = tuple(deepcopy_memo.keys())[0]
        old_deepcopy_memo_entry_id = id(deepcopy_memo[old_entry_memo_key])

    model_case.content_modify_func(model.content)
    model.validate_content()

    assert len(deepcopy_memo) == (
        model_case.deepcopy_memo_count if runtime.config.data.model.interactive else 0)

    if runtime.config.data.model.interactive:
        entry_memo_key = tuple(deepcopy_memo.keys())[0]
        assert entry_memo_key != old_entry_memo_key

        deepcopy_memo_entry_id = id(deepcopy_memo[entry_memo_key])
        assert deepcopy_memo_entry_id != old_deepcopy_memo_entry_id

    assert model.content == model_case.target_content


def test_snapshot_deepcopy_reuse_objects(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:
    def _inner_test_snapshot_deepcopy_reuse_objects() -> None:
        Model.data_class_creator.snapshot_holder.clear()

        inner = Model[list[int]]([2, 4])
        middle = Model[list[int | Model[list[int]]]]([1, 3, inner])
        outer = Model[list[int | Model[list[int | Model[list[int]]]]]]([0, middle, 5])

        inner.validate_content()
        middle.validate_content()
        outer.validate_content()

        # assert len(Model[int]().snapshot_holder) == 3
        # assert len(Model[int]().snapshot_holder._deepcopy_memo) == 3  # type: ignore[attr-defined]

        assert type(outer[1][-1]) is type(middle[-1]) is type(  # type: ignore[index]
            inner) is Model[list[int]]
        assert id(outer[1][-1]) == id(middle[-1]) == id(inner)  # type: ignore[index]

        assert type(outer.snapshot[1][-1]) is type(  # type: ignore[index]
            middle.snapshot[-1]) is Model[list[int]]
        assert id(outer.snapshot[1][-1]) == id(middle.snapshot[-1])  # type: ignore[index]

        assert type(outer[1][-1].content) is type(  # type: ignore[index]
            middle[-1].content) is type(  # type: ignore[index]
                inner.content) is list
        assert id(outer[1][-1].content) == id(middle[-1].content) == id(  # type: ignore[index]
            inner.content)

        assert type(outer.snapshot[1][-1].content) is type(  # type: ignore[index]
            middle.snapshot[-1].content) is type(inner.snapshot) is list
        assert id(outer.snapshot[1][-1].content) == id(  # type: ignore[index]
            middle.snapshot[-1].content) == id(inner.snapshot)

        assert type(outer[1].content) is type(middle.content) is list  # type: ignore[index]
        assert id(outer[1].content) == id(middle.content)  # type: ignore[index]

        assert type(outer.snapshot[1].content) is type(  # type: ignore[union-attr]
            middle.snapshot) is list
        assert id(outer.snapshot[1].content) == id(middle.snapshot)  # type: ignore[union-attr]

        del outer
        gc.collect()

    _inner_test_snapshot_deepcopy_reuse_objects()

    gc.collect()

    snapshot_holder = Model.data_class_creator.snapshot_holder
    snapshot_holder.delete_scheduled_deepcopy_content_ids()

    assert len(snapshot_holder) == 0
    assert len(snapshot_holder._deepcopy_memo) == 0  # type: ignore[attr-defined]


def test_snapshot_deepcopy_reuse_ids_crash(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    # for i in range(50):
    #     model_list = []
    #     for j in range(50):
    #         model = Model[list[int]]([])
    #         model.validate_content()
    #         model_list.append(model)

    class MyModel(Model[list[list[int]]]):
        ...

    for j in range(50):
        model = MyModel()
        model.from_data([[i] for i in range(500)])


def test_lazy_snapshot_not_triggered_by_set_content(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    model.content = ['abc']  # type: ignore[list-item]
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model.validate_content()
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model.validate_content()
    _assert_no_snapshot(model)

    model.content = [234]
    _assert_no_snapshot(model)

    model.validate_content()
    assert model.snapshot == model.content == [234]


def test_lazy_snapshot_not_triggered_by_state_keeping_operator(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    res_model = model + [234]  # type: ignore[operator]

    _assert_no_snapshot(model)
    assert model.content == [123]

    _assert_no_snapshot(res_model)
    assert res_model.content == [123, 234]


def test_lazy_snapshot_triggered_by_state_changing_operator(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model += ['abc']  # type: ignore[operator]
    assert model.snapshot == model.content == [123]

    model += [234]  # type: ignore[operator]
    assert model.snapshot == model.content == [123, 234]


def test_lazy_snapshot_not_triggered_by_getitem(
    skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture],
    skip_test_if_not_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    with pytest.raises(IndexError):
        model[1]  # type: ignore[index]

    _assert_no_snapshot(model)
    assert model.content == [123]

    res_model = model[0]  # type: ignore[index]

    _assert_no_snapshot(model)
    assert model.content == [123]

    _assert_no_snapshot(res_model)
    assert res_model.content == 123


def test_lazy_snapshot_triggered_by_setitem(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model[0] = ['abc']
    assert model.snapshot == model.content == [123]

    model[0] = 234
    assert model.snapshot == model.content == [234]


def test_lazy_snapshot_triggered_by_state_keeping_mimicked_methods(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    result = model.count(123)
    assert result == 1
    assert model.snapshot == model.content == [123]


def test_lazy_snapshot_triggered_by_state_changing_mimicked_methods(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model.append('abc')
    assert model.snapshot == model.content == [123]

    model.append(234)
    assert model.snapshot == model.content == [123, 234]


def test_lazy_snapshot_on_non_omnipy_pydantic_model_triggered_by_state_keeping_value_access(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:
    class SimplePydanticModel(pyd.BaseModel):
        value: Model[list[int]] = []

    model = Model[SimplePydanticModel](SimplePydanticModel(value=[123]))  # type: ignore[arg-type]
    _assert_no_snapshot(model)
    _assert_no_snapshot(model.content.value)

    # Just accessing a field of a pydantic model through __getattr__ is enough to trigger a snapshot
    # of the parent
    res_model = model.value
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[123])  # type: ignore[arg-type]

    _assert_no_snapshot(res_model)
    assert res_model.content == [123]


def test_lazy_snapshot_on_non_omnipy_pydantic_model_triggered_by_state_changing_value_access(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:
    class SimplePydanticModel(pyd.BaseModel):
        value: Model[list[int]] = []  # type: ignore[assignment]

    model = Model[SimplePydanticModel](SimplePydanticModel(value=[123]))  # type: ignore[arg-type]
    _assert_no_snapshot(model)

    # Trying to set the value of a field of a pydantic model also triggers a snapshot of the parent,
    # which here is used to for value reset
    with pytest.raises(ValidationError):
        model.value = ['abc']
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[123])  # type: ignore[arg-type]

    # The value of the field of the pydantic model is not changed, so no snapshot is triggered for
    # the child model.
    #
    # NB: Using model.content.value instead of value consequently for asserts to not trigger a
    # snapshot.
    assert model.content.value.content == [123]
    _assert_no_snapshot(model.content.value)

    # Trying to change the state of the child model in the field of a pydantic model triggers a
    # snapshot of the child (as well as of the parent due to the field access)
    with pytest.raises(ValidationError):
        model.value[0] = 'abc'
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[123])  # type: ignore[arg-type]
    assert model.content.value.snapshot == model.content.value.content == [123]

    # Here the value of the field of the pydantic model is set to a new non-model value, which
    # triggers validation and the creation of a new model to replace the old. The new model does not
    # have a snapshot by default
    model.value = [234]
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[234])  # type: ignore[arg-type]
    assert model.content.value.content == [234]
    _assert_no_snapshot(model.content.value)

    # Calling a method on the child model in the field of the pydantic model triggers a snapshot of
    # the child (as well as of the parent due to the field access). The snapshot is used to revert
    # from the incorrect state of the child model
    with pytest.raises(ValidationError):
        model.value.append('abc')
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[234])  # type: ignore[arg-type]
    assert model.content.value.snapshot == model.content.value.content == [234]

    # Calling a method on the child model in the field of the pydantic model triggers a snapshot of
    # the child (as well as of the parent due to the field access). Since the child model is in a
    # correct state, the value of the child model is updated, but validation creates a new list
    # that replaces the old one as the child model content, and a snapshot has been taken since all
    # method calls are considered potentially state-changing. Since the parent model refers to the
    # child model and not it's content, the values accessible the parent module are also
    # automatically updated. However, a snapshot is not taken (yet) for the parent model.

    model.value.append(345)
    assert model.content == SimplePydanticModel(value=[234, 345])  # type: ignore[arg-type]
    assert model.snapshot == SimplePydanticModel(value=[234])  # type: ignore[arg-type]

    assert model.content.value.snapshot == model.content.value.content == [234, 345]

    # Validating the parent model triggers snapshots for the parent, but not the child model.
    model.validate_content()
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[234, 345])  # type: ignore[arg-type]
    assert model.content.value.content == [234, 345]
    _assert_no_snapshot(model.content.value)

    # Validating the parent model triggers snapshots for both the parent and the child model.
    model.value.validate_content()
    assert model.snapshot == model.content \
           == SimplePydanticModel(value=[234, 345])  # type: ignore[arg-type]
    assert model.content.value.snapshot == model.content.value.content == [234, 345]


def test_snapshot_with_mimic_special_method(
        skip_test_if_not_interactive_mode: Annotated[None, pytest.fixture]) -> None:

    model = Model[list[int]]([123])

    _assert_no_snapshot(model)
    model.validate_content()

    assert model.snapshot == model.content == [123]
    assert model.snapshot_taken_of_same_model(model) is True
    assert model.snapshot_differs_from_model(model) is False
    assert model.content_validated_according_to_snapshot() is True

    first_snapshot_id = id(model.snapshot)
    assert first_snapshot_id != id(model.content)  # snapshot is copy of content

    with pytest.raises(ValidationError):
        model += ['abc']  # type: ignore[operator]

    assert model.snapshot == model.content == [123]
    assert model.snapshot_taken_of_same_model(model) is True
    assert model.snapshot_differs_from_model(model) is False
    assert model.content_validated_according_to_snapshot() is True

    model_copy = model.copy()
    _assert_no_snapshot(model_copy)
    assert model.snapshot == model_copy.content == [123]
    assert model.snapshot_taken_of_same_model(model_copy) is False
    assert model.snapshot_differs_from_model(model_copy) is False

    second_snapshot_id = id(model.snapshot)
    assert second_snapshot_id == first_snapshot_id

    model += [456]  # type: ignore[operator]

    assert model.snapshot == model.content == [123, 456]
    assert model.snapshot_taken_of_same_model(model) is True
    assert model.snapshot_differs_from_model(model) is False
    assert model.content_validated_according_to_snapshot() is True

    third_snapshot_id = id(model.snapshot)
    assert third_snapshot_id != second_snapshot_id

    model.validate_content()

    assert model.snapshot == model.content == [123, 456]
    assert model.snapshot_taken_of_same_model(model) is True
    assert model.content_validated_according_to_snapshot() is True

    fourth_snapshot_id = id(model.snapshot)
    assert fourth_snapshot_id != third_snapshot_id


def test_repeated_validation_should_not_change_content_or_snapshot(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    model = Model[list[int]]([123])

    id_content = None
    id_snapshot = None

    for i in range(2):
        model.validate_content()

        if id_content is not None:
            assert id(model.content) == id_content

        if runtime.config.data.model.interactive and id_snapshot is not None:
            assert id(model.snapshot) == id_snapshot


def test_mimic_special_method(
    runtime: Annotated[IsRuntime, pytest.fixture],
    skip_test_if_interactive_mode: Annotated[None, pytest.fixture],
) -> None:

    model = Model[list[int]]([123])
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model[0] = 'abc'

    assert_model(model, list[int], ['abc'])
    _assert_no_snapshot(model)

    # Since 'abc' is not rolled back, validation of all content fail, even though 456 validates
    with pytest.raises(ValidationError):
        model += [456]  # type: ignore[operator]

    assert_model(model, list[int], ['abc', 456])
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model += ['abc']  # type: ignore[operator]

    assert_model(model, list[int], ['abc', 456, 'abc'])
    _assert_no_snapshot(model)

    runtime.config.data.model.interactive = True
    _assert_no_snapshot(model)

    with pytest.raises(ValidationError):
        model.validate_content()

    # Deletion is rolled back as the model does not validate for the snapshot
    with pytest.raises(ValidationError):
        del model[-1]

    del model.content[-1]

    # Deletion is still rolled back as the model still does not validate for the snapshot
    with pytest.raises(ValidationError):
        del model[0]

    # Result of deletion now validates
    del model.content[0]
    model.validate_content()

    assert model.snapshot == model.content == [456]
    assert id(model.snapshot) != id(model.content)


def test_mimic_callable_with_exception(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    class MyClass:
        def __init__(self, number: int = 0):
            self.number = number

        def operate_with_error(self):
            self.number = -self.number
            raise RuntimeError('Self-destruct in 3... 2... 1...')

        def __eq__(self, other):
            return self.number == other.number

    model = Model[MyClass](MyClass(42))
    with pytest.raises(RuntimeError):
        model.operate_with_error()

    if runtime.config.data.model.interactive:
        assert model.snapshot == model.content == MyClass(42)
    else:
        assert model.content == MyClass(-42)


def test_mimic_validation_failure_recovery_with_interactive_mode(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    model = Model[list[int]]([12])
    assert model.content == [12]

    runtime.config.data.model.interactive = False
    with pytest.raises(ValidationError):
        model.append('abc')
    assert model.content == [12, 'abc']

    del model[-1]
    model.validate_content()
    runtime.config.data.model.interactive = True
    with pytest.raises(ValidationError):
        model.append('abc')
    assert model.content == [12]


def test_mimic_simple_list_operations(
        runtime: Annotated[IsRuntime, pytest.fixture],
        assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture]) -> None:

    model = Model[list[int]]()
    assert len(model) == 0

    model.append(123)
    assert len(model) == 1

    with pytest.raises(ValidationError):
        model.append('abc')

    if not runtime.config.data.model.interactive:
        assert_model(model, list[int], [123, 'abc'])
        del model[-1]

    assert_model(model, list[int], [123])
    assert_model_if_dyn_conv_else_val(model[0], int, 123)  # type: ignore[index]

    model += [234, 345, 456]  # type: ignore[operator]
    assert len(model) == 4

    assert_model_if_dyn_conv_else_val(model[-1], int, 456)  # type: ignore[index]
    assert_model(model[1:-1], list[int], [234, 345])  # type: ignore[index]

    assert tuple(reversed(model)) == (456, 345, 234, 123)

    model[2] = 432
    model[3] = '654'

    assert_model_if_dyn_conv_else_val(model[2], int, 432)  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(model[3], int, 654)  # type: ignore[index]

    with pytest.raises(ValidationError):
        model[0] = 'bacon'

    if not runtime.config.data.model.interactive:
        assert_model(model, list[int], ['bacon', 234, 432, 654])
        model[0] = 123

    assert_model_if_dyn_conv_else_val(model[1], int, 234)  # type: ignore[index]

    model[1] /= 2  # type: ignore[index]

    assert_model_if_dyn_conv_else_val(model[1], int, 117)  # type: ignore[index]
    assert_model(model, list[int], [123, 117, 432, 654])

    assert model.index(432) == 2

    assert model.pop() == 654
    assert len(model) == 3

    del model[-1]
    assert_model(model, list[int], [123, 117])

    del model[0:2]
    assert len(model) == 0


def test_mimic_simple_dict_operations(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    model = Model[dict[str, int]]({'abc': 123})

    assert len(model) == 1
    assert_model_if_dyn_conv_else_val(model['abc'], int, 123)  # type: ignore[index]

    model['abc'] = 321
    model['bcd'] = 234
    model['cde'] = 345

    with pytest.raises(ValidationError):
        model['def'] = 'eggs'

    if not runtime.config.data.model.interactive:
        assert 'def' in model
        del model['def']

    assert 'cde' in model  # type: ignore[operator]
    assert 'def' not in model  # type: ignore[operator]

    assert len(model) == 3
    assert_model(model, dict[str, int], {'abc': 321, 'bcd': 234, 'cde': 345})
    assert_model_if_dyn_conv_else_val(model['abc'], int, 321)  # type: ignore[index]

    model.update({'def': 456, 'efg': 567})
    assert 'def' in model  # type: ignore[operator]
    assert_model_if_dyn_conv_else_val(model['def'], int, 456)  # type: ignore[index]

    model |= {'efg': 765, 'ghi': 678}  # type: ignore[operator]
    assert_model_if_dyn_conv_else_val(model['efg'], int, 765)  # type: ignore[index]

    del model['bcd']

    other = {'abc': 321, 'cde': 345, 'def': 456, 'efg': 765, 'ghi': 678}
    assert_model(model, dict[str, int], other)


# TODO: Implement automatic conversion for mimicked operations, to allow for e.g.
#       `Model[int](1) + '1'`
# @pytest.mark.skipif(
#     os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
#     reason="""
# Mimicking operators only supports the same types as the original type, e.g. `Model[int](1) + '1'`
# still raises TypeError. This is also true for two Model instances, e.g.
# `Model[int](1) + Model[int](1)`. Should be relatively easy to support automatic validation of
# arguments as the same Model if `NotImplemented` Exception is raised from the operator method,
# e.g. `__add__()`.
# """)
def test_mimic_simple_list_operator_with_auto_convert(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    model = Model[list[int]]([0])

    #
    # model.__getitem__, model.__setitem__, model.__radd__, model[0].__add__, model[0].__sub__
    #

    model[0] += Model[int]('42')  # type: ignore[index]

    assert_model_if_dyn_conv_else_val(model[0], int, 42)  # type: ignore[index]
    assert_model(model, list[int], [42])

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        # model[0] is dynamically converted to a Model[int] instance
        model[0] += '42'  # type: ignore[index]

        assert_model(model[0], int, 84)  # type: ignore[index]
        assert_model(model, list[int], [84])

        model[0] -= '42'  # type: ignore[index]
    else:
        # model[0] is just an int
        with pytest.raises(TypeError):
            model[0] += '42'  # type: ignore[index]

    with pytest.raises(SyntaxError):
        eval("'42' += model[0]")

    with pytest.raises(TypeError):
        model[0] += 'abc'  # type: ignore[index]

    assert_model_if_dyn_conv_else_val(model[0], int, 42)  # type: ignore[index]
    assert_model(model, list[int], [42])

    #
    # model.__iadd__, model[0].__isub__
    #

    model += Model[list[int]](['42'])  # type: ignore[operator]
    assert_model(model, list[int], [42, 42])

    model += ['42']  # type: ignore[operator]
    assert_model(model, list[int], [42, 42, 42])

    with pytest.raises(SyntaxError):
        eval("['42'] += model")

    # No underlying TypeError, as any list can be added to a list. Exception is instead raised
    # during the subsequent validation of the content
    with pytest.raises(ValidationError):
        model += ['abc']  # type: ignore[operator]

    if runtime.config.data.model.interactive:
        assert_model(model, list[int], [42, 42, 42])
    else:
        assert_model(model, list[int], [42, 42, 42, 'abc'])
        del model[-1]

    #
    # model.__getitem__, model[0].__sub__,  model[0].__rsub__
    #

    ret = model[0] - Model[int]('42')  # type: ignore[index]
    assert_model(ret, int, 0)

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        # model[0] is dynamically converted to a Model[int] instance
        ret = model[0] - '42'  # type: ignore[index]
        assert_model(ret, int, 0)

        ret = '42' - model[0]  # type: ignore[index]
        assert_model(ret, int, 0)
    else:
        # model[0] is just an int
        with pytest.raises(TypeError):
            model[0] - '42'  # type: ignore[index]

        with pytest.raises(TypeError):
            '42' - model[0]  # type: ignore[index]

    with pytest.raises(TypeError):
        model[0] - 'abc'  # type: ignore[index]

    with pytest.raises(TypeError):
        'abc' - model[0]  # type: ignore[index]

    #
    # model.__add__,  model.__radd__
    #

    ret = model + Model[list[int]](['42'])  # type: ignore[operator]
    assert_model(ret, list[int], [42, 42, 42, 42])

    ret = model + ['42']  # type: ignore[operator]
    assert_model(ret, list[int], [42, 42, 42, 42])

    ret = ['42'] + model  # type: ignore[operator]
    assert_model(ret, list[int], [42, 42, 42, 42])

    with pytest.raises(TypeError):
        model + 'abc'  # type: ignore[operator]

    with pytest.raises(TypeError):
        'abc' + model  # type: ignore[operator]


def test_mimic_hash_method():
    hashable_model = Model[str]('Hello World!')
    assert hash(hashable_model) != 0

    unhashable_model = Model[list[int]]()
    with pytest.raises(TypeError):
        hash(unhashable_model)


def test_mimic_model_as_bool():
    default_model = Model[bool]()
    assert True if not default_model else False

    false_model = Model[bool](False)
    assert True if not false_model else False

    true_model = Model[bool](True)
    assert True if true_model else False

    class MyClass:
        ...

    myclass_model = Model[MyClass]()
    assert True if myclass_model else False


def test_mimic_call_method():
    callable_model = Model[Callable](lambda x: x + 1)

    assert callable_model(1) == 2

    class MyClass:
        ...

    not_callable_class_model = Model[MyClass]()
    with pytest.raises(TypeError):
        not_callable_class_model(1)

    not_callable_builtin_model = Model[int]()
    with pytest.raises(TypeError):
        not_callable_builtin_model(1)


def test_mimic_sequence_convert_for_concat(
    runtime: Annotated[IsRuntime, pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
) -> None:
    runtime.config.data.model.interactive = True

    # SetDeque is used as an example of non-builtin Sequence type. to_data() is needed (for now)
    # to allow model conversion to list/tuple.

    # TODO: Revise the need for to_data() method when explicit conversion types are supported
    #       Should in this case be something like Model[SetDeque, list]

    class SetDequeModel(Model[SetDeque[int] | list[int]]):
        @classmethod
        def _parse_data(cls, data: SetDeque[int] | list[int]) -> SetDeque[int]:
            return SetDeque(data)

        def to_data(self) -> object:
            return list(self.content)

    my_list = [1, 2, 3]
    my_tuple = (4, 5, 6)
    my_setdeque: SetDeque[int] = SetDeque([7, 8, 9])

    my_list_model = Model[list](my_list)
    my_tuple_model = Model[tuple](my_tuple)
    my_setdeque_model = SetDequeModel(my_setdeque)

    #
    # Raw object concatenation
    #

    with pytest.raises(TypeError):
        my_list + my_tuple  # type: ignore[operator]

    with pytest.raises(TypeError):
        my_list + my_setdeque  # type: ignore[operator]

    with pytest.raises(TypeError):
        my_tuple + my_list  # type: ignore[operator]

    with pytest.raises(TypeError):
        my_tuple + my_setdeque  # type: ignore[operator]

    with pytest.raises(TypeError):
        my_setdeque + my_list  # type: ignore[operator]

    with pytest.raises(TypeError):
        my_setdeque + my_tuple  # type: ignore[operator]

    #
    # Model concatenation
    #

    assert_model(
        my_list_model + my_tuple_model,  # type: ignore[operator]
        list,
        [1, 2, 3, 4, 5, 6])
    assert_model(
        my_list_model + my_setdeque_model,  # type: ignore[operator]
        list,
        [1, 2, 3, 7, 8, 9])
    assert_model(
        my_tuple_model + my_list_model,  # type: ignore[operator]
        tuple,
        (4, 5, 6, 1, 2, 3))
    assert_model(
        my_tuple_model + my_setdeque_model,  # type: ignore[operator]
        tuple,
        (4, 5, 6, 7, 8, 9))
    assert_model(
        my_setdeque_model + my_list_model,  # type: ignore[operator]
        SetDeque[int] | list[int],
        SetDeque((7, 8, 9, 1, 2, 3)))
    assert_model(
        my_setdeque_model + my_tuple_model,  # type: ignore[operator]
        SetDeque[int] | list[int],
        SetDeque((7, 8, 9, 4, 5, 6)))

    #
    # Model + raw object concatenation
    #

    assert_model(
        my_list_model + my_tuple,  # type: ignore[operator]
        list,
        [1, 2, 3, 4, 5, 6])
    assert_model(my_list_model + my_setdeque, list, [1, 2, 3, 7, 8, 9])  # type: ignore[operator]
    assert_model(
        my_tuple_model + my_list,  # type: ignore[operator]
        tuple,
        (4, 5, 6, 1, 2, 3))
    assert_model(my_tuple_model + my_setdeque, tuple, (4, 5, 6, 7, 8, 9))  # type: ignore[operator]
    assert_model(
        my_setdeque_model + my_list,  # type: ignore[operator]
        SetDeque[int] | list[int],
        SetDeque((7, 8, 9, 1, 2, 3)))
    assert_model(
        my_setdeque_model + my_tuple,  # type: ignore[operator]
        SetDeque[int] | list[int],
        SetDeque((7, 8, 9, 4, 5, 6)))

    #
    # Raw object + Model concatenation
    #

    assert_model(
        my_list + my_tuple_model,  # type: ignore[operator]
        tuple,
        (1, 2, 3, 4, 5, 6))
    assert_model(
        my_list + my_setdeque_model,  # type: ignore[operator]
        SetDeque[int] | list[int],
        SetDeque((1, 2, 3, 7, 8, 9)))
    assert_model(
        my_tuple + my_list_model,  # type: ignore[operator]
        list,
        [4, 5, 6, 1, 2, 3])
    assert_model(
        my_tuple + my_setdeque_model,  # type: ignore[operator]
        SetDeque[int] | list[int],
        SetDeque((4, 5, 6, 7, 8, 9)))
    assert_model(my_setdeque + my_list_model, list, [7, 8, 9, 1, 2, 3])  # type: ignore[operator]
    assert_model(my_setdeque + my_tuple_model, tuple, (7, 8, 9, 4, 5, 6))  # type: ignore[operator]


def test_mimic_concatenation_for_strings(
    runtime: Annotated[IsRuntime, pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
) -> None:

    help = UppercaseModel('help')
    assert help.content == 'HELP'

    stream = 'Can you ' + 'please ' + help + ' me?'
    stream += " I've fallen and I can't get up!"

    assert isinstance(stream, UppercaseModel)
    assert stream.content == "CAN YOU PLEASE HELP ME? I'VE FALLEN AND I CAN'T GET UP!"


def test_mimic_concatenation_for_converted_models(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    please_help = WordSplitterModel('please help')
    assert please_help.content == ['please', 'help']

    stream = 'Can you ' + please_help + ' me?'
    stream += "I've fallen"

    assert isinstance(stream, WordSplitterModel)
    assert stream.content == "Can you please help me? I've fallen".split()

    stream += ['and'] + ['I']
    stream += UppercaseModel("can't get up!")

    assert isinstance(stream, WordSplitterModel)
    assert stream.content == [
        'Can', 'you', 'please', 'help', 'me?', "I've", 'fallen', 'and', 'I', "CAN'T", 'GET', 'UP!'
    ]

    new_stream = ['Someone', 'is', 'shouting:'] + stream + (
        UppercaseModel('- We should') + ' help them!')

    assert isinstance(new_stream, WordSplitterModel)
    if runtime.config.data.model.dynamically_convert_elements_to_models:
        joined_str = ' '.join(new_stream.content)
    else:
        joined_str = ' '.join(new_stream)
    assert joined_str == ('Someone is shouting: Can you please help me? '
                          "I've fallen and I CAN'T GET UP! - WE SHOULD HELP THEM!")

    assert_model_if_dyn_conv_else_val(new_stream[5], str, 'please')

    sentence = new_stream[3:8]
    sentence.insert(2, 'pretty')

    assert isinstance(sentence, WordSplitterModel)
    assert sentence.content == ['Can', 'you', 'pretty', 'please', 'help', 'me?']


def test_mimic_concatenation_for_converted_models_with_incompatible_content_except_to_data(
) -> None:
    assert not issubclass(MyList, list)
    assert not issubclass(MyList, Sequence)

    class MyListOfUppercaseModel(Model[MyList[UppercaseModel] | WordSplitterModel]):
        @classmethod
        def _parse_data(cls,
                        data: MyList[UppercaseModel] | WordSplitterModel) -> MyList[UppercaseModel]:
            if isinstance(data, WordSplitterModel):
                return MyList(*(UppercaseModel(word) for word in data.content))
            return data

        # A custom to_data() method is needed to allow for compatibility
        def to_data(self) -> object:
            return [el.to_data() for el in self.content.data]

    MyListOfUppercaseModel(MyList(UppercaseModel('Can'), UppercaseModel('you')))

    # content of WordSplitterModel are compatible with MyListOfUppercaseModel
    stream = MyListOfUppercaseModel('Can you please') + WordSplitterModel('be silent!')
    assert stream.to_data() == ['CAN', 'YOU', 'PLEASE', 'BE', 'SILENT!']

    # content of MyListOfUppercaseModel are incompatible with WordSplitterModel
    stream = WordSplitterModel('We will, we will') + MyListOfUppercaseModel('rock you!')
    assert stream.to_data() == ['We', 'will,', 'we', 'will', 'ROCK', 'YOU!']


def test_mimic_str_concat_iadd_and_radd_overrides_add_if_defined(
        skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture]):
    # Only __add__

    class ConcatChallengedStr:
        def __init__(self, data: str = ''):
            self._data = data

        def __repr__(self):
            return self._data

        def __eq__(self, other):
            return self._data == other

    class NarcissisticStr(ConcatChallengedStr):
        def __add__(self, other: object) -> 'NarcissisticStr':
            return self

    T = TypeVar('T', default=ConcatChallengedStr)

    class ConcatChallengedStrModel(Model[T | str], Generic[T]):
        @classmethod
        def _parse_data(cls, data: T | str) -> T:
            union_type = cls.outer_type(with_args=True)
            str_variant_type = get_args(union_type)[0]
            if not isinstance(data, str_variant_type):
                return str_variant_type(data)
            return data

    class NarcissisticStrModel(ConcatChallengedStrModel[NarcissisticStr]):
        ...

    narcissistic_str_model = NarcissisticStrModel('Me and only me!')

    new_narcissistic_str_model = narcissistic_str_model + 'I am also here...'
    assert isinstance(new_narcissistic_str_model, NarcissisticStrModel)
    assert narcissistic_str_model.content == 'Me and only me!'

    narcissistic_str_model += 'I am also here...'
    assert narcissistic_str_model.content == 'Me and only me!'

    other_narcissistic_str_model = 'Me, me me!' + narcissistic_str_model
    assert isinstance(other_narcissistic_str_model, NarcissisticStrModel)
    assert other_narcissistic_str_model.content == 'Me, me me!'

    # Only __iadd__ and __radd__
    class GrumpyStr(ConcatChallengedStr):
        def __iadd__(self, other: object) -> 'GrumpyStr':
            raise ValueError('Go away!')

        def __radd__(self, other: object) -> 'GrumpyStr':
            raise RuntimeError("Don't stand in front of me!")

    class GrumpyStrModel(ConcatChallengedStrModel[GrumpyStr]):
        ...

    grumpy_str_model = GrumpyStrModel('Hrmpf!')

    with pytest.raises(TypeError):
        grumpy_str_model + 'Excuse me...'

    with pytest.raises(ValueError):
        grumpy_str_model += ('Sorry, but...')

    with pytest.raises(RuntimeError):
        'I just wondered...?' + grumpy_str_model

    # All of __add__, __iadd__ and __radd__
    class GrumpyNarcissisticStr(GrumpyStr, NarcissisticStr):
        ...

    class GrumpyNarcissisticStrModel(ConcatChallengedStrModel[GrumpyNarcissisticStr]):
        ...

    grumpy_narcissistic_str_model = GrumpyNarcissisticStrModel('Me and only me! Hmrpf!')

    new_grumpy_narcissistic_str_model = grumpy_narcissistic_str_model + 'And perhaps also me?'
    assert isinstance(new_grumpy_narcissistic_str_model, GrumpyNarcissisticStrModel)
    assert new_grumpy_narcissistic_str_model.content == 'Me and only me! Hmrpf!'

    with pytest.raises(ValueError):
        grumpy_narcissistic_str_model += ('Sorry, but...')

    with pytest.raises(RuntimeError):
        'I just wondered...?' + grumpy_narcissistic_str_model


@pc.fixture
@pc.parametrize('other_type_out', [False, True], ids=['same_type_out', 'other_type_out'])
@pc.parametrize('other_type_in', [False, True], ids=['same_type_in', 'other_type_in'])
@pc.parametrize('has_iadd', [False, True], ids=['no_iadd', 'has_iadd'])
@pc.parametrize('has_radd', [False, True], ids=['no_radd', 'has_radd'])
@pc.parametrize('has_add', [False, True], ids=['no_add', 'has_add'])
def all_add_variants(has_add: bool,
                     has_radd: bool,
                     has_iadd: bool,
                     other_type_in: bool,
                     other_type_out: bool) -> tuple[bool, bool, bool, bool, bool]:
    return has_add, has_radd, has_iadd, other_type_in, other_type_out


@pc.fixture
def all_less_than_five_model_add_variants(  # noqa: C901
        all_add_variants: Annotated[tuple[bool, bool, bool, bool, bool], pytest.fixture],):
    has_add, has_radd, has_iadd, other_type_in, other_type_out = all_add_variants

    ENGLISH_TO_NUMBER = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
    NUMBER_TO_ENGLISH = {1: 'one', 2: 'two', 3: 'three', 4: 'four'}

    class MyNumber(MyNumberBase):
        ...

    def _common_adder(self,
                      adder_func: Callable[[MyNumber, MyNumber], MyNumber],
                      other: MyNumber | str) -> MyNumber | str | NotImplementedType:
        ret: MyNumber | str | NotImplementedType
        if isinstance(other, str):
            converted = ENGLISH_TO_NUMBER.get(other)
            if other_type_in and converted is not None:
                other = MyNumber(converted)
            else:
                return NotImplemented

        ret = adder_func(self, other)

        if other_type_out:
            if ret.val in NUMBER_TO_ENGLISH:
                return NUMBER_TO_ENGLISH[ret.val]
            else:
                return NotImplemented
        else:
            return ret

    def _add(self, other: MyNumber | str) -> MyNumber | str | NotImplementedType:
        def _add_func(self: MyNumber, other: MyNumber) -> MyNumber:
            return MyNumber(self.val + other.val)

        return _common_adder(self, _add_func, other)

    def _radd(self, other: MyNumber | str) -> MyNumber | str | NotImplementedType:
        def _radd_func(self: MyNumber, other: MyNumber) -> MyNumber:
            return MyNumber(other.val + self.val)

        return _common_adder(self, _radd_func, other)

    def _iadd(self, other: MyNumber | str) -> MyNumber | str | NotImplementedType:
        def _iadd_func(self: MyNumber, other: MyNumber) -> MyNumber:
            self.val += other.val
            return self

        return _common_adder(self, _iadd_func, other)

    if has_add:
        setattr(MyNumber, '__add__', _add)

    if has_radd:
        setattr(MyNumber, '__radd__', _radd)

    if has_iadd:
        setattr(MyNumber, '__iadd__', _iadd)

    class LessThanFiveModel(Model[MyNumber | int]):
        @classmethod
        def _parse_data(cls, data: MyNumber | int) -> MyNumber:
            my_num = MyNumber(data) if isinstance(data, int) else data
            assert my_num.val < 5
            return my_num

    return LessThanFiveModel(1)


def test_mimic_add_concat_all_less_than_five_model_add_variants(
    all_add_variants: Annotated[tuple[bool, bool, bool, bool, bool], pytest.fixture],
    all_less_than_five_model_add_variants: Annotated[Model[MyNumberBase], pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
):
    has_add, has_radd, has_iadd, other_type_in, other_type_out = all_add_variants
    less_than_five_model = all_less_than_five_model_add_variants

    assert less_than_five_model.content.val == 1

    if has_add:
        with pytest.raises(TypeError):
            less_than_five_model.__add__(1, 2)

        with pytest.raises(TypeError):
            less_than_five_model.__add__(1, no_such_kwarg=True)

        res = less_than_five_model + ('three' if other_type_in else 3)  # type: ignore[operator]
        if other_type_out:
            assert res == 'four'
        else:
            assert res.content.val == 4
    else:
        with pytest.raises(TypeError):
            less_than_five_model + ('three' if other_type_in else 3)  # type: ignore[operator]


def test_mimic_radd_concat_all_less_than_five_model_add_variants(
    all_add_variants: Annotated[tuple[bool, bool, bool, bool, bool], pytest.fixture],
    all_less_than_five_model_add_variants: Annotated[Model[MyNumberBase], pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
):
    has_add, has_radd, has_iadd, other_type_in, other_type_out = all_add_variants
    less_than_five_model = all_less_than_five_model_add_variants

    assert less_than_five_model.content.val == 1

    if any((has_radd, has_add)):
        with pytest.raises(TypeError):
            less_than_five_model.__radd__(1, 2)

        with pytest.raises(TypeError):
            less_than_five_model.__radd__(1, no_such_kwarg=True)

        res = ('two' if other_type_in else 2) + less_than_five_model  # type: ignore[operator]
        if other_type_out:
            assert res == 'three'
        else:
            assert res.content.val == 3
    else:
        with pytest.raises(TypeError):
            ('two' if other_type_in else 2) + less_than_five_model  # type: ignore[operator]


def test_mimic_iadd_concat_all_less_than_five_model_add_variants(
    all_add_variants: Annotated[tuple[bool, bool, bool, bool, bool], pytest.fixture],
    all_less_than_five_model_add_variants: Annotated[Model[MyNumberBase], pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
):
    has_add, has_radd, has_iadd, other_type_in, other_type_out = all_add_variants
    less_than_five_model = all_less_than_five_model_add_variants

    assert less_than_five_model.content.val == 1

    if any((has_iadd, has_add)):
        with pytest.raises(TypeError):
            less_than_five_model.__iadd__(1, 2)

        with pytest.raises(TypeError):
            less_than_five_model.__iadd__(1, no_such_kwarg=True)

        if not other_type_out:
            less_than_five_model += 'one' if other_type_in else 1  # type: ignore[operator]
            assert less_than_five_model.content.val == 2
    else:
        with pytest.raises(TypeError):
            less_than_five_model += 'one' if other_type_in else 1  # type: ignore[operator]


# Logically covers cases such as `Model[list[int]]([123]) + ['abc']` (and '+' operator variants)
def test_mimic_concat_less_than_five_model_add_variants_with_other_type_in_and_invalid_result(
    all_add_variants: Annotated[tuple[bool, bool, bool, bool, bool], pytest.fixture],
    all_less_than_five_model_add_variants: Annotated[Model[MyNumberBase], pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
):
    has_add, has_radd, has_iadd, other_type_in, other_type_out = all_add_variants
    less_than_five_model = all_less_than_five_model_add_variants

    assert less_than_five_model.content.val == 1

    if not other_type_in or not any((has_add, has_radd, has_iadd)):
        pytest.skip('Not relevant combination for this test')

    # MyNumberBase.__add__() and variants does support adding 'four', but this breaks validation of
    # LessThanFiveModel

    if has_add:
        with pytest.raises(TypeError if other_type_out else ValidationError):
            less_than_five_model + 'four'  # type: ignore[operator]

    if any((has_radd, has_add)):
        with pytest.raises(TypeError if other_type_out else ValidationError):
            'four' + less_than_five_model  # type: ignore[operator]

    if any((has_iadd, has_add)):
        with pytest.raises(TypeError if other_type_out else ValidationError):
            less_than_five_model += 'four'  # type: ignore[operator]


def test_mimic_concat_all_less_than_five_model_add_variants_with_unsupported_input(
    all_add_variants: Annotated[tuple[bool, bool, bool, bool, bool], pytest.fixture],
    all_less_than_five_model_add_variants: Annotated[Model[MyNumberBase], pytest.fixture],
    skip_test_if_dynamically_convert_elements_to_models: Annotated[None, pytest.fixture],
):
    has_add, has_radd, has_iadd, other_type_in, other_type_out = all_add_variants
    less_than_five_model = all_less_than_five_model_add_variants

    assert less_than_five_model.content.val == 1

    # MyNumberBase.__add__() and variants do not support adding 'five'
    with pytest.raises(TypeError):
        less_than_five_model + 'five'  # type: ignore[operator]

    with pytest.raises(TypeError):
        'five' + less_than_five_model  # type: ignore[operator]

    with pytest.raises(TypeError):
        less_than_five_model += 'five'  # type: ignore[operator]


def test_mimic_first_level_operations_on_nested_list(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    model = Model[list[int | list[int]]]([123, 234, [345]])

    model[-1] = []
    assert_model(model, list[int | list[int]], [123, 234, []])

    with pytest.raises(ValidationError):
        model[-1] = 'abc'

    with pytest.raises(ValidationError):
        model[-1] = None

    with pytest.raises(ValidationError):
        model[-1] = {2: 3}

    with pytest.raises(ValidationError):
        model[-1] = {}

    with pytest.raises(ValidationError):
        model[-1] = ['abc', 'bce']


def test_mimic_first_level_operations_on_nested_dict() -> None:
    model = Model[dict[str, dict[int, int] | int]]({'a': {12: 234, 13: 345}})

    # empty list is parsed as empty dict in pydantic v1
    model['a'] = []
    assert_model(model, dict[str, dict[int, int] | int], {'a': {}})

    with pytest.raises(ValidationError):
        model['a'] = 'abc'

    with pytest.raises(ValidationError):
        model['a'] = None

    with pytest.raises(ValidationError):
        model['a'] = ['abc']

    with pytest.raises(ValidationError):
        model['a'] = {'abc': 'bce'}


def test_mimic_nested_list_operations_only_model_at_top(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    model = Model[list[int | list[int]]]([123, 234, [345]])

    model[-1] = tuple(range(3))

    assert_model(model, list[int | list[int]], [123, 234, [0, 1, 2]])
    assert_model_if_dyn_conv_else_val(model[0], int, 123)  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(model[-1], list[int], [0, 1, 2])  # type: ignore[index]

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        with pytest.raises(ValidationError):
            model[-1].append(tuple(range(3)))  # type: ignore[index]

        assert len(model[-1]) == 3  # type: ignore[index]
        assert_model(model[-1], list[int], [0, 1, 2])  # type: ignore[index]
        assert_model(model[-1][-1], int, 2)  # type: ignore[index]

        with pytest.raises(ValidationError):
            model[-1][-1] = 'a'  # type: ignore[index]
        # model[-1] creates a new Model[list[int]] object each time, so changes do not propagate to
        # parent. See `test_mimic_doubly_nested_dyn_converted_containers_are_copies`
        model[-1][-1] = '3'  # type: ignore[index]
        assert_model(model[-1][-1], int, 2)  # type: ignore[index]
    else:
        # model[-1] is a regular list and not a model. Changes propagate as one would expect, but
        # manual validation is needed.
        model[-1][-1] = '3'  # type: ignore[index]
        assert_val(model[-1][-1], str, '3')  # type: ignore[index]
        model.validate_content()
        assert_val(model[-1][-1], int, 3)  # type: ignore[index]

    model[0] = [0, 2]
    assert_model_if_dyn_conv_else_val(model[0], list[int], [0, 2])  # type: ignore[index]

    # Here the `model[0] +=` operation is a series of `__getitem__`, `__iadd__`, and `__setitem__`
    # operations, with the `__getitem__` and `__setitem__` operating on the "parent" model object,
    # causing ValidationError even when `dynamically_convert_elements_to_models` is disabled.
    with pytest.raises(ValidationError):
        model[0] += ('a',)  # type: ignore[index]

    if not runtime.config.data.model.dynamically_convert_elements_to_models \
            and not runtime.config.data.model.interactive:
        assert_val(model[0], list[int], [0, 2, 'a'])  # type: ignore[index]
        del model[0][-1]
    assert_model_if_dyn_conv_else_val(model[0], list[int], [0, 2])  # type: ignore[index]

    # In contrast to the `+` operator, the `append()` method only operates on the child level
    # (on the result of the `__getitem__()` call). When `dynamically_convert_elements_to_models` is
    # disabled, this is simply a plain Python list (without any validation). When
    # `dynamically_convert_elements_to_models` is enabled, however, the results of the
    # `__getitem__()` call is automatically converted to a new Model[int]() object, which then
    # validates its content.
    if runtime.config.data.model.dynamically_convert_elements_to_models:
        with pytest.raises(ValidationError):
            model[0].append('a')  # type: ignore[index]

        # Validation error happens on the dynamically created submodel, which is then destroyed.
        # This is the reason the value seems reverted even when model.interactive is False...!
        # See `test_mimic_doubly_nested_dyn_converted_containers_are_copies`
        assert_model(model[0], list[int], [0, 2])  # type: ignore[index]
    else:
        model[0].append('a')  # type: ignore[index]
        with pytest.raises(ValidationError):
            model.validate_content()

        if not runtime.config.data.model.interactive:
            assert_val(model[0], list, [0, 2, 'a'])  # type: ignore[index]
            del model[0][-1]
        assert_val(model[0], list, [0, 2])  # type: ignore[index]

    two_as_bytes = model[0][-1].to_bytes(4, byteorder='little')  # type: ignore[index]
    assert_val(two_as_bytes, bytes, b'\x02\x00\x00\x00')


def test_mimic_nested_list_operations_models_at_all_levels(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    # Compare with `test_mimic_nested_dict_operations_only_model_at_top`. It is recommended to
    # insert a model at every level except the last when working with nested structures.

    NestedModelType: TypeAlias = list[int | Model[list[int]]]
    model = Model[NestedModelType]([123, 234, [345]])

    model[-1] = tuple(range(3))

    assert_model(model, NestedModelType, [123, 234, Model[list[int]]([0, 1, 2])])
    assert_model_if_dyn_conv_else_val(model[0], int, 123)  # type: ignore[index]
    assert_model(model[-1], list[int], [0, 1, 2])  # type: ignore[index]

    model[-1][-1] = '3'  # type: ignore[index]
    assert_model_if_dyn_conv_else_val(model[-1][-1], int, 3)  # type: ignore[index]

    model[0] = [0, 2]
    assert_model(model[0], list[int], [0, 2])  # type: ignore[index]

    # The user do not have to care about the difference between the '+=' operator and the 'append' ,
    # method, as in `test_mimic_nested_list_operations_only_model_at_top`
    with pytest.raises(ValidationError):
        model[0] += ('a',)  # type: ignore[index]

    if not runtime.config.data.model.interactive:
        assert_model(model[0], list[int], [0, 2, 'a'])  # type: ignore[index]
        del model[0][-1]

    assert_model(model[0], list[int], [0, 2])  # type: ignore[index]

    with pytest.raises(ValidationError):
        model[0].append('a')  # type: ignore[index]

    if not runtime.config.data.model.interactive:
        assert_model(model[0], list[int], [0, 2, 'a'])  # type: ignore[index]
        del model[0][-1]

    assert_model(model[0], list[int], [0, 2])  # type: ignore[index]

    two_as_bytes = model[0][-1].to_bytes(4, byteorder='little')  # type: ignore[index]
    assert_val(two_as_bytes, bytes, b'\x02\x00\x00\x00')


def test_mimic_nested_dict_operations_only_model_at_top(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    model = Model[dict[str, dict[int, int] | int]]({'a': {14: 456}})

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        submodel_a = model['a']  # type: ignore[index]

        with pytest.raises(ValidationError):
            submodel_a.update({'14': '654', '15': {'a': 'b'}})

        if not runtime.config.data.model.interactive:
            assert_model_if_dyn_conv_else_val(
                submodel_a,
                dict[int, int],
                {
                    14: 456, '14': '654', '15': dict(a='b')
                },
            )
            del submodel_a['15']
            assert_model_if_dyn_conv_else_val(submodel_a, dict[int, int], {14: 654})
            submodel_a[14] = 456

        assert len(submodel_a) == 1
        assert_model(submodel_a, dict[int, int], {14: 456})

        # Changes above have all been made on copies, see
        # test_mimic_doubly_nested_dyn_converted_containers_are_copies()
        assert len(model['a']) == 1  # type: ignore[index]

        # Same with updates directly on model['a']
        model['a'].update({'14': '654', '15': '333'})  # type: ignore[index]
        assert len(model['a']) == 1  # type: ignore[index]

        assert_model(model['a'], dict[int, int], {14: 456})  # type: ignore[index]
        assert_model(model, dict[str, dict[int, int] | int], {'a': {14: 456}})
    else:
        subdict_a = model['a']  # type: ignore[index]

        # As model['a'] is not a Model, update() does not validate
        subdict_a.update({'14': '654', '15': {'a': 'b'}})

        assert len(subdict_a) == 3
        assert_val(subdict_a, dict, {14: 456, '14': '654', '15': {'a': 'b'}})

        # With dynamic conversion disabled, subdict_a is not a copy
        assert len(model['a']) == 3  # type: ignore[index]

        # Disabling dynamic conversion also allows for direct updates on model['a'], as normal, but
        # the values are still not validated
        model['a'].update({'14': '654', '15': '333'})  # type: ignore[index]
        assert_val(model['a'], dict, {14: 456, '14': '654', '15': '333'})
        model.validate_content()
        assert_val(model['a'], dict, {14: 654, 15: 333})


def test_mimic_nested_dict_operations_models_at_all_levels(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    # Compare with `test_mimic_nested_dict_operations_only_model_at_top`. It is recommended to
    # insert a model at every level except the last when working with nested structures.

    NestedModelType: TypeAlias = dict[str, Model[dict[int, int]] | int]
    model = Model[NestedModelType]({'a': {14: 456}})

    with pytest.raises(ValidationError):
        model['a'].update({'14': '654', '15': {'a': 'b'}})

    if not runtime.config.data.model.interactive:
        assert_model(model['a'], dict[int, int], {14: 456, '14': '654', '15': {'a': 'b'}})
        del model['a']['15']
        assert_model(model['a'], dict[int, int], {14: 654})
        model['a'][14] = 456

    assert_model(model['a'], dict[int, int], {14: 456})  # type: ignore[index]
    assert_model(model, NestedModelType, {'a': Model[dict[int, int]]({14: 456})})

    model['a'].update({'14': '654', '15': '333'})  # type: ignore[index]
    assert_model(model['a'], dict[int, int], {14: 654, 15: 333})
    assert_model(model, NestedModelType, {'a': Model[dict[int, int]]({14: 654, 15: 333})})


def test_mimic_list_and_dict_iterators(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    list_model = Model[list[int]]([0, 1, 2])

    for i, el in enumerate(list_model):
        assert_model_if_dyn_conv_else_val(el, int, i)

    dict_model = Model[dict[int, str]]({0: 'abc', 1: 'bcd', 2: 'cde'})

    assert tuple(dict_model.keys()) == (0, 1, 2)

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        assert tuple(dict_model.values()) == (Model[str]('abc'),
                                              Model[str]('bcd'),
                                              Model[str]('cde'))
        assert tuple(dict_model.items()) == ((0, Model[str]('abc')), (1, Model[str]('bcd')),
                                             (2, Model[str]('cde')))
    else:
        assert tuple(dict_model.values()) == ('abc', 'bcd', 'cde')
        assert tuple(dict_model.items()) == ((0, 'abc'), (1, 'bcd'), (2, 'cde'))

    for i, key in enumerate(dict_model):
        assert_model_if_dyn_conv_else_val(key, int, i)


def test_mimic_doubly_nested_dyn_converted_containers_are_copies(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:

    list_model = Model[list[list[int]]]([[4]])
    assert_model_if_dyn_conv_else_val(list_model[0], list[int], [4])  # type: ignore[index]

    inner_list = list_model[0]  # type: ignore[index]
    inner_list.append(5)

    assert_model_if_dyn_conv_else_val(inner_list, list[int], [4, 5])

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        # Dynamically converted nested containers are copies
        assert_model(list_model[0], list[int], [4])  # type: ignore[index]
        assert_model(list_model, list[list[int]], [[4]])
    else:
        # Without dynamic conversion, the nested containers are not copies
        assert_val(list_model[0], list[int], [4, 5])  # type: ignore[index]
        assert_model(list_model, list[list[int]], [[4, 5]])

    dict_model = Model[dict[int, dict[int, int]]]({0: {1: 1}})
    assert_model_if_dyn_conv_else_val(dict_model[0], dict[int, int], {1: 1})  # type: ignore[index]

    inner_dict = dict_model[0]  # type: ignore[index]
    inner_dict.update({2: 2})

    assert_model_if_dyn_conv_else_val(inner_dict, dict[int, int], {1: 1, 2: 2})

    if runtime.config.data.model.dynamically_convert_elements_to_models:
        assert_model(dict_model[0], dict[int, int], {1: 1})  # type: ignore[index]
        assert_model(dict_model, dict[int, dict[int, int]], {0: {1: 1}})
    else:
        assert_val(dict_model[0], dict[int, int], {1: 1, 2: 2})  # type: ignore[index]
        assert_model(dict_model, dict[int, dict[int, int]], {0: {1: 1, 2: 2}})


def test_mimic_nested_list_operations_with_model_subclass_containers(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_model_if_dyn_conv_else_val: Annotated[AssertModelOrValFunc, pytest.fixture],
) -> None:
    # See test_mimic_doubly_nested_dyn_converted_containers_are_copies()
    # Explicit Model containers fixes this issue.

    class MyListOrIntModel(Model[list[int] | int]):
        ...

    class MyListModel(Model[list[MyListOrIntModel]]):
        ...

    model = MyListModel([123, 234, [345]])

    model[-1] = tuple(range(3))
    assert len(model[-1]) == 3

    with pytest.raises(TypeError):
        len(model[0])

    assert_model(
        model,
        list[MyListOrIntModel],
        [MyListOrIntModel(123), MyListOrIntModel(234), MyListOrIntModel([0, 1, 2])],
    )
    assert_model(
        model[-1],  # type: ignore[index]
        list[int] | int,
        [0, 1, 2],
    )

    assert_model_if_dyn_conv_else_val(model[-1][-1], int, 2)  # type: ignore[index]

    class MyListDoubleModel(Model[Model[list[int]]]):
        ...

    double_model = MyListDoubleModel([123])
    assert_model_if_dyn_conv_else_val(double_model[0], int, 123)  # type: ignore[index]


def test_mimic_nested_dict_operations_with_model_containers(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    # See test_mimic_doubly_nested_dyn_converted_containers_are_copies()
    # Explicit Model containers fixes this issue.

    ThirdLvl: TypeAlias = dict[int, int]
    SecondLvl: TypeAlias = dict[int, Model[ThirdLvl] | int] | int
    FirstLvl: TypeAlias = dict[str, Model[SecondLvl]]
    model = Model[FirstLvl]({'a': {12: 234, 13: 345}})

    with pytest.raises(ValidationError):
        model['a'] = 'abc'

    with pytest.raises(ValidationError):
        model['a'] = None

    with pytest.raises(ValidationError):
        model['a'] = ['abc']

    model['a'] = []
    assert_model(model['a'], SecondLvl, {})  # type: ignore[index]

    with pytest.raises(ValidationError):
        model['a'] = {'abc': 'bce'}

    model['a'] = {'14': '456'}
    assert model.to_data() == ({'a': {14: 456}})

    assert_model(model, FirstLvl, {'a': Model[SecondLvl]({14: 456})})
    assert_model(model['a'], SecondLvl, {14: 456})  # type: ignore[index]

    with pytest.raises(ValidationError):
        model['a'].update({'14': '654', '15': {'a': 'b'}})  # type: ignore[index]

    with pytest.raises(ValidationError):
        model['a'].update({'14': '654', '15': {'111': {1: 2}}})  # type: ignore[index]

    if not runtime.config.data.model.interactive:
        assert_model(model['a'], SecondLvl, {14: 456, '14': '654', '15': {'111': {1: 2}}})
        del model['a']['15']
        assert_model(model['a'], SecondLvl, {14: 654})
        model['a'][14] = 456

    assert len(model['a']) == 1  # type: ignore[index]
    assert_model(model, FirstLvl, {'a': Model[SecondLvl]({14: 456})})

    model['a'].update({'14': '654', '15': {'111': 4321}})  # type: ignore[index]

    assert len(model['a']) == 2  # type: ignore[index]
    content_1 = {'a': Model[SecondLvl]({14: 654, 15: Model[ThirdLvl]({111: 4321})})}
    assert_model(model, FirstLvl, content_1)

    with pytest.raises(ValidationError):
        model['a'] |= {'16': {'a': 'b'}}  # type: ignore[index]

    model['a'] |= {'16': {'112': 5432}}  # type: ignore[index]
    content_2 = {
        'a':
            Model[SecondLvl]({
                14: 654,
                15: Model[ThirdLvl]({
                    111: 4321
                }),
                16: Model[ThirdLvl]({
                    112: 5432
                }),
            })
    }
    assert_model(model, FirstLvl, content_2)

    with pytest.raises(ValidationError):
        model['a'][15] |= {112: tuple(range(3))}  # type: ignore[index]

    with pytest.raises(ValidationError):
        model['a'][15] |= {'112': 'a'}  # type: ignore[index]

    with pytest.raises(ValidationError):
        model['a'][15] |= {'112': []}  # type: ignore[index]

    with pytest.raises(ValidationError):
        model['a'][15][111] = []  # type: ignore[index]

    model['a'][15] = []  # type: ignore[index]
    content_3 = {
        'a': Model[SecondLvl]({
            14: 654,
            15: Model[ThirdLvl]({}),
            16: Model[ThirdLvl]({
                112: 5432
            }),
        })
    }
    assert_model(model, FirstLvl, content_3)


def test_mimic_doubly_nested_union(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:

    runtime.config.data.model.dynamically_convert_elements_to_models = True

    list_model = Model[list[list[int]] | list[list[str]]]([[4]])
    assert_model(list_model[0], list[int], [4])  # type: ignore[index]

    with pytest.raises(ValidationError):
        list_model[0][0] = 'four'  # type: ignore[index]

    list_model[0] = ['four']
    assert_model(list_model[0], list[str], ['four'])  # type: ignore[index]

    dict_model = Model[dict[int, dict[int, int]] | dict[int, dict[str, str]]]({0: {1: 1}})
    assert_model(dict_model[0], dict[int, int], {1: 1})  # type: ignore[index]

    with pytest.raises(ValidationError):
        dict_model[0][0] = 'zero'  # type: ignore[index]

    dict_model[0] = {0: 'zero'}
    assert_model(dict_model[0], dict[str, str], {'0': 'zero'})  # type: ignore[index]


def test_mimic_operations_as_scalars() -> None:
    int_model = Model[int](1)

    assert (int_model + 1).content == 2  # type: ignore[operator, attr-defined]
    assert (1 + int_model).content == 2  # type: ignore[operator, attr-defined]
    assert int_model.content == 1

    int_model *= 10  # type: ignore[operator, assignment]
    assert int_model.content == 10

    # converting to other basic type removes Model
    assert int_model / 3 == pytest.approx(3.333333)  # type: ignore[operator]
    assert (int_model // 3).content == 3  # type: ignore[operator, attr-defined]
    assert -int_model.content == -10

    # modulo
    assert (int_model % 3).content == 1  # type: ignore[operator, attr-defined]
    # bitwise AND
    assert (int_model & 2).content == 2  # type: ignore[operator, attr-defined]
    # power
    assert (int_model**2).content == 100  # type: ignore[operator]

    assert float(int_model) == float(10)  # converting to other basic type removes Model

    float_model = Model[float](10)
    assert (float_model / 3).content == pytest.approx(  # type: ignore[operator, attr-defined]
        3.333333)

    float_model_2 = Model[float](2.5)
    assert floor(float_model_2) == 2  # converting to other basic type removes Model


def test_mimic_operations_as_union_of_scalars() -> None:
    model = Model[int | float](1)

    assert (model + 1).content == 2  # type: ignore[operator, attr-defined]
    assert (1 + model).content == 2  # type: ignore[operator, attr-defined]
    assert model.content == 1

    model *= 10  # type: ignore[operator, assignment]
    assert model.content == 10

    assert (model / 3).content == pytest.approx(3.333333)  # type: ignore[operator, attr-defined]
    assert (model // 3).content == 3  # type: ignore[operator, attr-defined]
    assert -model.content == -10

    # modulo
    assert (model % 3).content == 1  # type: ignore[operator, attr-defined]
    # bitwise AND
    assert (model & 2).content == 2  # type: ignore[operator, attr-defined]
    # power
    assert (model**2).content == 100  # type: ignore[operator]

    assert float(model) == 10  # float(), int(), etc always converts


def test_mimic_operations_on_pydantic_models() -> None:
    T = TypeVar('T')

    class ParentPydanticModel(pyd.BaseModel):
        a: int = 0

    class ChildPydanticModel(ParentPydanticModel):
        b: str = ''

    class GenericPydanticModel(pyd.GenericModel, Generic[T]):
        a: T | None = None

    class ChildGenericPydanticModel(GenericPydanticModel[int]):
        b: str = ''

    parent_pydantic_model = Model[ParentPydanticModel]()
    assert parent_pydantic_model.a == 0
    parent_pydantic_model.a = 2
    assert parent_pydantic_model.a == 2
    parent_pydantic_model.a = '2'
    assert parent_pydantic_model.a == 2
    with pytest.raises(ValidationError):
        parent_pydantic_model.a = 'abc'

    child_pydantic_model = Model[ChildPydanticModel]()
    assert child_pydantic_model.a == 0
    assert child_pydantic_model.b == ''
    child_pydantic_model.b = 'someone else'
    assert child_pydantic_model.b == 'someone else'
    child_pydantic_model.b = 123
    assert child_pydantic_model.b == '123'

    generic_pydantic_model = Model[GenericPydanticModel[int]]()
    assert generic_pydantic_model.a is None
    parent_pydantic_model.a = '2'
    assert parent_pydantic_model.a == 2
    with pytest.raises(ValidationError):
        parent_pydantic_model.a = 'abc'

    child_generic_pydantic_model = Model[ChildGenericPydanticModel]()
    assert child_generic_pydantic_model.a is None
    child_generic_pydantic_model.a = '2'
    assert child_generic_pydantic_model.a == 2
    assert child_generic_pydantic_model.b == ''
    child_generic_pydantic_model.b = 123
    assert child_generic_pydantic_model.b == '123'


# TODO: Add support in Model for mimicking the setting and deletion of properties
# def test_mimic_property() -> None:
#     class MyMetadata:
#         def __init__(self) -> None:
#             self._metadata: str | None = 'metadata'
#
#         @property
#         def metadata(self):
#             return self._metadata
#
#         @metadata.setter
#         def metadata(self, value: str | None):
#             self._metadata = value
#
#             if value is None:
#                 raise ValueError('Not allowed to reset to None')
#
#         @metadata.deleter
#         def metadata(self):
#             self._metadata = None
#             raise ValueError('Not allowed to delete metadata')
#
#
#     model = Model[MyMetadata]()
#     assert model.metadata == 'metadata'
#
#     model.metadata = 'my metadata'
#     assert model.metadata == 'my metadata'
#
#     with pytest.raises(ValueError):
#         model.metadata = None
#
#     assert model.metadata == 'my metadata'
#
#     with pytest.raises(ValueError):
#         del model.metadata
#     assert model.metadata == 'my metadata'


def test_mimic_callable_property() -> None:
    # Example of previously failing callable property is pandas.DataFrame.loc

    class MyCallable:
        def __init__(self):
            self.called = False

        def __call__(self):
            self.called = True

    class MyCallableHolder:
        def __init__(self) -> None:
            self._func: Callable = MyCallable()

        @property
        def func(self) -> Callable:
            return self._func

    model = Model[MyCallableHolder]()
    assert model.func.called is False


# TODO: Revisit test_mimic_object_member_not_in_class_known_issue() is mimicking of __setattr__ is
#       implemented. Libraries like Pandas might also graft methods onto instances such as
#       DataFrames, which will not currently work with Omnipy. Dynamically added member variables
#       that are not bound methods do work, however.
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue due to validation of the model content before the calling of the method when
model.interactive is set to True. Since the method is grafted onto the specific model instance, it
is bound to that instance only. However, validation shallow-copies the instance, including the
method, but does not rebind the method to the new instance. The result is that the method is
called on the old instance, and not the new one.

Conclusion: avoid grafting methods onto models instances. Dynamically grafting methods is in any
case an advanced operation and does not follow Python best practices. Grafting instance variables
or unbound methods should work as expected, see test_mimic_dynamically_bound_instance_variable.
""")
def test_mimic_dynamically_bound_instance_method_known_issue(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    class MyClass:
        def __init__(self) -> None:
            self.called = False

    my_obj = MyClass()
    my_obj.method = MethodType(  # type: ignore[attr-defined]
        lambda self: setattr(self, 'called', True), my_obj)

    model = Model[MyClass](my_obj)
    assert model.called is False

    model.method()

    if runtime.config.data.model.interactive:
        assert (my_obj.called, model.called) == (False, True)
    else:
        assert (my_obj.called, model.called) == (True, True)


def test_mimic_dynamically_bound_instance_variable(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    class MyClass:
        def toggle_if_available(self) -> None:
            if hasattr(self, 'toggle'):
                self.toggle = not self.toggle  # type: ignore[has-type]

    my_obj = MyClass()
    my_obj.toggle = False

    model = Model[MyClass](my_obj)
    assert model.toggle is False

    model.toggle_if_available()

    if runtime.config.data.model.interactive:
        assert (my_obj.toggle, model.toggle) == (False, True)
    else:
        assert (my_obj.toggle, model.toggle) == (True, True)


def test_literal_model_defaults() -> None:
    assert LiteralFiveModel().to_data() == 5
    assert LiteralFiveModel().outer_type(with_args=True) is Literal[5]

    assert LiteralTextModel().to_data() == 'text'
    assert LiteralTextModel().outer_type(with_args=True) is Literal['text']

    assert LiteralFiveOrTextModel().to_data() == 5
    assert LiteralFiveOrTextModel().outer_type(with_args=True) is Literal[5, 'text']


def test_literal_model_validation() -> None:
    with pytest.raises(ValidationError):
        LiteralFiveModel(4)

    with pytest.raises(ValidationError):
        LiteralTextModel('txt')

    with pytest.raises(ValidationError):
        LiteralFiveOrTextModel(4)

    with pytest.raises(ValidationError):
        LiteralFiveOrTextModel('txt')


def test_mimic_operations_on_literal_models() -> None:
    assert LiteralFiveModel(5) / 5 == 1
    with pytest.raises(AttributeError):
        LiteralFiveModel().upper()

    assert LiteralTextModel().upper() == 'TEXT'

    assert_model(LiteralTextModel('text') + '', Literal['text'], 'text')
    assert_val(LiteralTextModel('text') + '.txt', str, 'text.txt')

    # Here, LiteralTextModel.__add__() fails, while Model[str].__radd__() saves the day!
    assert LiteralTextModel('text') + Model[str]('.txt') == Model[str]('text.txt')

    with pytest.raises(TypeError):
        LiteralTextModel() / 2

    assert LiteralFiveOrTextModel() + 5 == 10
    assert LiteralFiveOrTextModel('text').upper() == 'TEXT'

    with pytest.raises(AttributeError):
        LiteralFiveOrTextModel().upper()

    with pytest.raises(TypeError):
        LiteralFiveOrTextModel('text') / 2


def test_json_schema_generic_model_one_level() -> None:
    ListT = TypeVar('ListT', bound=list, default=list)

    # Note that the TypeVars need to be bound to a type who in itself, or whose origin_type
    # produces a default value when called without parameters. Here, `ListT` is bound to list,
    # and `typing.get_origin(list)() == []`.

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    assert MyList.to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyList",
      "description": "My very interesting list model!",
      "type": "array",
      "items": {}
    }""")

    assert MyList[list].to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyList[list]",
      "description": "My very interesting list model!",
      "type": "array",
      "items": {}
    }""")


def test_json_schema_generic_model_two_levels() -> None:
    StrT = TypeVar('StrT', bound=str)

    class MyListOfStrings(Model[list[StrT]], Generic[StrT]):
        """My very own list of strings!"""

    assert MyListOfStrings.to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyListOfStrings",
      "description": "My very own list of strings!",
      "type": "array",
      "items": {
        "type": "string"
      }
    }""")

    assert MyListOfStrings[str].to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyListOfStrings[str]",
      "description": "My very own list of strings!",
      "type": "array",
      "items": {
        "type": "string"
      }
    }""")


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue due to shortcomings of the typing standard library.
Class variables of generic classes are not all available in
in runtime (see: https://github.com/python/typing/issues/629)
In this case, the description of the generic class MyList
is not available from MyListOfStrings to_json_schema method.
Any workarounds should best be implemented in pydantic,
possibly in omnipy if this becomes a real issue.
""")
def test_json_schema_generic_models_known_issue() -> None:
    ListT = TypeVar('ListT', bound=list)

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    class MyListOfStrings(Model[MyList[list[str]]]):
        """MyList. What more can you ask for?"""

    assert MyListOfStrings.to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyListOfStrings",
      "description": "MyList. What more can you ask for?",
      "$ref": "#/definitions/MyList_List_str__",
      "definitions": {
        "MyList_List_str__": {
          "title": "MyList[list[str]]",
          "description": "My very interesting list model!.",
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }""")


def test_custom_parser() -> None:
    class UpperCaseStr(Model[str]):
        @classmethod
        def _parse_data(cls, data: str) -> str:
            return data.upper()

    assert UpperCaseStr('help').to_data() == 'HELP'

    model = UpperCaseStr()
    assert model.to_data() == ''

    model.from_data('I need somebody!')
    assert model.to_data() == 'I NEED SOMEBODY!'


def test_custom_parser_and_validation() -> None:
    class OnlyUpperCaseLettersStr(Model[str]):
        @classmethod
        def _parse_data(cls, data: str) -> str:
            assert data == '' or data.isalpha()
            return data.upper()

    assert OnlyUpperCaseLettersStr('help').to_data() == 'HELP'

    model = OnlyUpperCaseLettersStr()
    model.from_data('Notjustanybody')
    assert model.to_data() == 'NOTJUSTANYBODY'

    with pytest.raises(ValidationError):
        OnlyUpperCaseLettersStr('Help!')

    with pytest.raises(ValidationError):
        model = OnlyUpperCaseLettersStr()
        model.from_data('Not just anybody! Call 911!!')


def test_custom_parser_to_other_type() -> None:
    from .helpers.models import StringToLength

    assert StringToLength('So we sailed up to the sun').to_data() == 26
    string_to_length = StringToLength()
    string_to_length.from_data('Till we found the sea of green')
    assert string_to_length.to_data() == 30


def test_nested_model() -> None:
    class DictToListOfPositiveInts(Model[dict[pyd.PositiveInt, list[pyd.PositiveInt]]]):
        """This model is perfect for a mapping product numbers to factor lists"""

    model_1 = DictToListOfPositiveInts()
    assert model_1.to_data() == {}

    product_factors = {
        2: [2], 3: [3], 4: [2, 2], 5: [5], 6: [2, 3], 7: [7], 8: [2, 2, 2], 9: [3, 3]
    }
    model_1.from_data(product_factors)
    assert model_1.to_data() == product_factors

    unloaded_data = model_1.to_data()
    unloaded_data[10] = [-2, -5]  # type: ignore[index]

    with pytest.raises(ValidationError):
        model_1.from_data(unloaded_data)

    unloaded_data[10] = [2, 5]  # type: ignore[index]
    model_1.from_data(unloaded_data)
    assert model_1.to_data() == unloaded_data

    assert model_1.to_json(
        pretty=False) == ('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                          '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')

    model_2 = DictToListOfPositiveInts()
    model_2.from_json('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                      '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')
    assert sorted(model_2.to_data()) == sorted({  # type: ignore[call-overload]
        2: [2],
        3: [3],
        4: [2, 2],
        5: [5],
        6: [2, 3],
        7: [7],
        8: [2, 2, 2],
        9: [3, 3],
        10: [2, 5]
    })

    assert model_1.to_json_schema() == dedent("""\
    {
      "title": "DictToListOfPositiveInts",
      "description": "This model is perfect for a mapping product numbers to factor lists",
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "integer",
          "exclusiveMinimum": 0
        }
      }
    }""")


def test_complex_nested_models() -> None:
    class ProductFactorsTuple(Model[tuple[pyd.PositiveInt, list[pyd.PositiveInt]]]):
        """This model maps a single product to its product_factors, including validation"""
        @classmethod
        def _parse_data(
            cls, data: tuple[pyd.PositiveInt, list[pyd.PositiveInt]]
        ) -> tuple[pyd.PositiveInt, list[pyd.PositiveInt]]:
            from functools import reduce
            from operator import mul

            product, factors = data
            assert reduce(mul, factors) == product
            return data

    class ListOfProductFactorsTuples(Model[list[ProductFactorsTuple]]):
        """A list of ProductFactorsTuples"""

    model = ListOfProductFactorsTuples()
    assert model.to_data() == []

    product_factors_as_tuples = [(2, [2]), (3, [3]), (4, [2, 2]), (5, [5]), (6, [2, 3]), (7, [7]),
                                 (8, [2, 2, 2]), (9, [3, 3])]

    model.from_data(product_factors_as_tuples)
    assert model.to_data() == product_factors_as_tuples

    unloaded_data = model.to_data()
    unloaded_data.append((10, [3, 5]))  # type: ignore[attr-defined]

    with pytest.raises(ValidationError):
        model.from_data(unloaded_data)

    unloaded_data[-1] = (10, [2, 5])  # type: ignore[index]
    model.from_data(unloaded_data)

    assert model.to_data() == unloaded_data

    roman_numerals = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X')

    # TODO: As part of redesign of parse methods in Model, consider to make sure that parsers where
    #       the typing allows output can be directly funnelled back as input, but which still change
    #       the data, can be revalidated without altering the state. An example of such a Model is
    #       the RomanNumeral Model below, given that the if statement where removed.
    class RomanNumeral(Model[str]):
        """A roman numeral"""
        @classmethod
        def _parse_data(cls, data: str) -> str:
            if data in roman_numerals:
                return data
            number = int(data)
            assert 0 < number <= 10
            return roman_numerals[number - 1]

    class ListOfProductFactorsTuplesRoman(Model[list[tuple[RomanNumeral, list[RomanNumeral]]]]):
        """A list of ProductFactorsTuples with RomanNumerals"""

    class ProductFactorDictInRomanNumerals(Model[dict[str, list[str]]]):
        """Extremely useful model"""

    roman_tuple_model = ListOfProductFactorsTuplesRoman(unloaded_data)
    roman_dict_model_1 = ProductFactorDictInRomanNumerals(roman_tuple_model.to_data())

    assert roman_dict_model_1.to_json(
        pretty=False) == ('{"II": ["II"], "III": ["III"], "IV": ["II", "II"], "V": ["V"], '
                          '"VI": ["II", "III"], "VII": ["VII"], "VIII": ["II", "II", "II"], '
                          '"IX": ["III", "III"], "X": ["II", "V"]}')

    roman_dict_model_2 = ProductFactorDictInRomanNumerals()
    roman_dict_model_2.from_json('{"II": ["II"], "III": ["III"], "IV": ["II", "II"], "V": ["V"], '
                                 '"VI": ["II", "III"], "VII": ["VII"], "VIII": ["II", "II", "II"], '
                                 '"IX": ["III", "III"], "X": ["II", "V"]}')
    assert roman_dict_model_2.to_data() == {
        'II': ['II'],
        'III': ['III'],
        'IV': ['II', 'II'],
        'V': ['V'],
        'VI': ['II', 'III'],
        'VII': ['VII'],
        'VIII': ['II', 'II', 'II'],
        'IX': ['III', 'III'],
        'X': ['II', 'V']
    }

    assert roman_dict_model_1.to_json_schema() == dedent("""\
    {
      "title": "ProductFactorDictInRomanNumerals",
      "description": "Extremely useful model",
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    }""")


def test_pandas_dataframe_non_builtin_direct() -> None:
    # TODO: Using pandas here to test concept of non-builtin data structures. Switch to other
    #  example to remove dependency, to prepare splitting of pandas module to separate repo
    #
    # SetDeque() is a good candidate.

    from omnipy.components.pandas.lazy_import import pd

    class PandasDataFrameModel(Model[pd.DataFrame]):
        ...

    dataframe = pd.DataFrame([[1, 2, 3], [4, 5, 6]])

    model_1 = PandasDataFrameModel()
    assert isinstance(model_1.content, pd.DataFrame) and model_1.content.empty

    model_1.content = dataframe

    pd.testing.assert_frame_equal(
        model_1.content,
        dataframe,
    )

    with pytest.raises(ValidationError):
        PandasDataFrameModel([[1, 2, 3], [4, 5, 6]])

    model_2 = PandasDataFrameModel(dataframe)

    pd.testing.assert_frame_equal(
        model_2.content,
        dataframe,
    )


def test_non_builtin_model_with_parser() -> None:
    class PathModelWithParser(Model[MyPath | str]):
        @classmethod
        def _parse_data(cls, data: MyPath | str) -> MyPath:
            if isinstance(data, str):
                return MyPath(data)
            return data

        def to_data(self) -> str:
            return str(self.content)

        def __str__(self):
            return str(self.content)

    _assert_path_model(PathModelWithParser)

    str_path = PathModelWithParser('tests/data')
    assert isinstance(str_path.content, MyPath)
    assert str_path.content == MyPath('tests/data')
    assert str_path.to_data() == 'tests/data'
    assert str(str_path) == 'tests/data'

    int_path = PathModelWithParser(123)
    assert int_path.content == MyPath('123')
    assert int_path.to_data() == '123'
    assert str(int_path) == '123'


def test_non_builtin_model_with_from_data() -> None:
    class PathModelWithFromData(Model[MyPath]):
        def from_data(self, value: MyPath | str) -> None:
            if isinstance(value, str):
                self._validate_and_set_value(MyPath(value))
            else:
                self._validate_and_set_value(value)

        def to_data(self) -> str:
            return str(self.content)

        def __str__(self):
            return str(self.content)

    _assert_path_model(PathModelWithFromData)

    with pytest.raises(ValidationError):
        PathModelWithFromData('tests/data')

    with pytest.raises(ValidationError):
        PathModelWithFromData(123)


def _assert_path_model(PathModel: type[IsModel[MyPath]]) -> None:
    path = PathModel()
    assert isinstance(path.content, MyPath)
    assert path.content == MyPath()
    assert path.to_data() == '.'
    assert str(path) == '.'
    path.from_data('tests/data')
    assert isinstance(path.content, MyPath)
    assert path.content == MyPath('tests/data')
    new_path = path / 'test_model.py'
    assert isinstance(new_path, PathModel)
    assert new_path.content == MyPath('tests/data/test_model.py')
    assert str(new_path) == 'tests/data/test_model.py'


def test_non_builtin_model_with_custom_default_value() -> None:
    # Hack to provide a custom default value for models where calling the root type without
    # arguments does not produce a default value.
    class DefaultDatetime(datetime):
        def __new__(cls, *args, **kwargs):
            if len(args) == 0:
                return datetime.min
            return datetime.__new__(datetime, *args, **kwargs)

    class DatetimeModel(Model[DefaultDatetime | datetime | str]):
        @classmethod
        def _parse_data(cls, data: datetime | str) -> datetime:
            if isinstance(data, str):
                return datetime.fromisoformat(data)
            return data

    event_time = datetime(year=2024, month=5, day=17, hour=8)

    model = DatetimeModel()
    assert isinstance(model.content, datetime)
    assert model.content == datetime.min
    assert model.to_data() == datetime.min

    model.from_data('2024-05-17T08:00:00')
    assert isinstance(model.content, datetime)
    assert model.content == event_time
    assert model.to_data() == event_time

    model.from_data(event_time)
    assert isinstance(model.content, datetime)
    assert model.content == event_time
    assert model.to_data() == event_time


def test_parametrized_model() -> None:
    assert ParamUpperStrModel().content == ''
    assert ParamUpperStrModel('foo').content == 'foo'

    MyUpperStrModel = ParamUpperStrModel.adjust('MyUpperStrModel', upper=True)
    assert MyUpperStrModel('bar').content == 'BAR'

    model = ParamUpperStrModel()

    model.from_data('foo')
    assert model.content == 'foo'

    upper_model = MyUpperStrModel()
    upper_model.from_data('bar')
    assert upper_model.content == 'BAR'

    model.from_json('"foobar"')
    assert model.content == 'foobar'

    upper_model.from_json('"foobar"')
    assert upper_model.content == 'FOOBAR'

    with pytest.raises(AttributeError):
        ParamUpperStrModel.adjust('MyUpperStrModel', True)

    MyLowerStrModel = ParamUpperStrModel.adjust('MyLowerStrModel', upper=False)
    assert MyLowerStrModel('bar').content == 'bar'


def test_parametrized_model_wrong_keyword() -> None:
    with pytest.raises(KeyError):
        ParamUpperStrModel.adjust('ParamSupperStrModel', supper=True)


def test_parametrized_model_with_none() -> None:
    with pytest.raises(ValidationError):
        ParamUpperStrModel(None)

    MyUpperStrModel = ParamUpperStrModel.adjust('MyUpperStrModel', upper=True)

    with pytest.raises(ValidationError):
        MyUpperStrModel(None)

    assert DefaultStrModel(None).content == 'default'

    DefaultOtherStrModel = DefaultStrModel.adjust('DefaultOtherStrModel', default='other')

    assert DefaultOtherStrModel(None).content == 'other'
