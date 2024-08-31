from dataclasses import dataclass
import os
from typing import Annotated

from pydantic import ValidationError
from pydantic.fields import Field
import pytest

from omnipy.data.param import ParamsBase


def test_params_parameter_lookup(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @dataclass(kw_only=True)
    class MyParams(ParamsBase):
        my_int: int = 123
        my_str: str = "abc"

    assert MyParams.my_int == 123
    assert MyParams.my_str == "abc"

    with pytest.raises(AttributeError):
        MyParams.something_else

    assert not hasattr(MyParams, 'something_else')
    assert hasattr(MyParams, 'validate')


def test_params_parameter_value_is_read_only(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @dataclass(kw_only=True)
    class MyParams(ParamsBase):
        my_int: int = 123
        my_str: str = "abc"

    with pytest.raises(AttributeError):
        MyParams.my_int = 456

    with pytest.raises(AttributeError):
        MyParams.something_else = 456

    MyParams.__abstractmethods__ = frozenset()


def test_params_default_value_validation(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @dataclass(kw_only=True)
    class MyClass:
        def __init__(self, a: int):
            self.a = a

        def __eq__(self, other: object) -> bool:
            return isinstance(other, MyClass) and self.a == other.a

    with pytest.raises(ValidationError):

        @dataclass(kw_only=True)
        class MyFailingParams(ParamsBase):
            my_int: int = '123'  # type: ignore[assignment]
            my_str: str = 456  # type: ignore[assignment]
            my_obj: MyClass = 123  # type: ignore[assignment]

    my_default_obj = MyClass(123)

    @dataclass(kw_only=True)
    class MyParams(ParamsBase):
        my_int: int = '123'  # type: ignore[assignment]
        my_str: str = 456  # type: ignore[assignment]
        my_obj: MyClass = my_default_obj

    assert MyParams.my_int == 123
    assert MyParams.my_str == '456'
    assert MyParams.my_obj == my_default_obj
    assert MyParams.my_obj is not my_default_obj

    with pytest.raises(ValueError):

        class MyDefaultFactoryParams(ParamsBase):
            my_id: int = Field(default_factory=lambda: 123)


# TODO: Check if test_params_default_value_validation_known_issue can be removed after pydantic v2
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Due to a pydantic v1 "feature" which sets the type of a field to Optional[<type>] when default is
None, instead if raising a ValidationError.
""")
def test_params_default_value_validation_known_issue(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    class MyClass:
        ...

    with pytest.raises(ValidationError):

        @dataclass(kw_only=True)
        class MyFailingParams(ParamsBase):
            my_obj: MyClass = None  # type: ignore[assignment]


def test_params_no_default_value(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):

        @dataclass(kw_only=True)
        class MyParams(ParamsBase):
            my_str: str
            my_int: int = 123

    class MyParamsWithNone(ParamsBase):
        my_none: None = None
        my_str_or_none: str | None = None


def test_params_validation(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @dataclass(kw_only=True)
    class MyParams(ParamsBase):
        my_int: int = 123
        my_str: str = "abc"

    with pytest.raises(RuntimeError):
        MyParams()

    with pytest.raises(RuntimeError):
        MyParams(my_int=456, my_str='cde')


def test_params_copy_and_adjust(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    class MyClass:
        def __init__(self, a: int):
            self.a = a

        def __eq__(self, other: object) -> bool:
            return isinstance(other, MyClass) and self.a == other.a

    my_default_obj = MyClass(123)

    @dataclass(kw_only=True)
    class MyParams(ParamsBase):
        my_int_or_float: int | float = 123
        my_str_or_none: str | None = None
        my_obj: MyClass = my_default_obj

    MyNewParams = MyParams.copy_and_adjust('MyNewParams')
    assert MyNewParams.__name__ == 'MyNewParams'
    assert MyNewParams.my_int_or_float == 123
    assert MyNewParams.my_str_or_none == None
    assert MyNewParams.my_obj == my_default_obj
    assert MyNewParams.my_obj is not my_default_obj

    MyOtherParams = MyParams.copy_and_adjust('MyThirdParams', my_int_or_float=456)
    assert MyOtherParams.__name__ == 'MyThirdParams'
    assert MyOtherParams.my_int_or_float == 456
    assert MyOtherParams.my_str_or_none is None
    assert MyOtherParams.my_obj == my_default_obj
    assert MyOtherParams.my_obj is not my_default_obj

    my_new_obj = MyClass(234)
    MyThirdParams = MyParams.copy_and_adjust(
        'MyThirdParams',
        my_int_or_float=456.3,
        my_str_or_none=789,
        my_obj=my_new_obj,
    )
    assert MyThirdParams.__name__ == 'MyThirdParams'
    assert MyThirdParams.my_int_or_float == 456.3
    assert MyThirdParams.my_str_or_none == '789'
    assert MyThirdParams.my_obj == my_new_obj
    assert MyThirdParams.my_obj is not my_new_obj
    assert MyParams.my_obj == my_default_obj

    with pytest.raises(ValidationError):
        MyParams.copy_and_adjust('MyFailingParams', my_int_or_float='abc', my_str_or_none='abc')

    with pytest.raises(TypeError):
        MyParams.copy_and_adjust('MyFailingParams', 456)  # type: ignore[call-arg]