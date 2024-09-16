import os
from typing import Annotated

from pydantic import BaseModel, ValidationError
from pydantic.fields import Field
import pytest

from omnipy.data.param import params_dataclass, ParamsBase


def test_params_parameter_lookup(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @params_dataclass
    class MyParams(ParamsBase):
        my_int: int = 123
        my_str: str = 'abc'

    assert MyParams.my_int == 123
    assert MyParams.my_str == 'abc'

    with pytest.raises(AttributeError):
        MyParams.something_else

    assert not hasattr(MyParams, 'something_else')
    assert hasattr(MyParams, 'validate')


def test_params_parameter_value_is_read_only(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @params_dataclass
    class MyParams(ParamsBase):
        my_int: int = 123
        my_str: str = 'abc'

    with pytest.raises(AttributeError):
        MyParams.my_int = 456

    with pytest.raises(AttributeError):
        MyParams.something_else = 456

    MyParams.__abstractmethods__ = frozenset()


def test_params_default_value_validation(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    class MyPydanticModel(BaseModel):
        a: str
        b: int

    with pytest.raises(ValidationError):

        @params_dataclass
        class MyFailingParams(ParamsBase):
            my_int: int = '123'  # type: ignore[assignment]
            my_str: str = 456  # type: ignore[assignment]
            my_model: type[BaseModel] = 123  # type: ignore[assignment]

    @params_dataclass
    class MyParams(ParamsBase):
        my_int: int = '123'  # type: ignore[assignment]
        my_str: str = 456  # type: ignore[assignment]
        my_model: type[BaseModel] = MyPydanticModel

    assert MyParams.my_int == 123
    assert MyParams.my_str == '456'
    assert MyParams.my_model is MyPydanticModel

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

        @params_dataclass
        class MyFailingParams(ParamsBase):
            my_obj: MyClass = None  # type: ignore[assignment]


def test_params_no_default_value(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):

        @params_dataclass
        class MyParams(ParamsBase):
            my_str: str
            my_int: int = 123

    class MyParamsWithNone(ParamsBase):
        my_none: None = None
        my_str_or_none: str | None = None


def test_params_validation(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    @params_dataclass
    class MyParams(ParamsBase):
        my_int: int = 123
        my_str: str = 'abc'

    with pytest.raises(RuntimeError):
        MyParams()

    with pytest.raises(RuntimeError):
        MyParams(my_int=456, my_str='cde')


def test_params_copy_and_adjust(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    class MyPydanticModel(BaseModel):
        a: str
        b: int

    @params_dataclass
    class MyParams(ParamsBase):
        my_int_or_float: int | float = 123
        my_str_or_none: str | None = None
        my_model: type[BaseModel] = MyPydanticModel

    MyNewParams = MyParams.copy_and_adjust('MyNewParams')
    assert MyNewParams.__name__ == 'MyNewParams'
    assert MyNewParams.my_int_or_float == 123
    assert MyNewParams.my_str_or_none is None
    assert MyNewParams.my_model is MyPydanticModel

    MyOtherParams = MyParams.copy_and_adjust('MyOtherParams', my_int_or_float=456)
    assert MyOtherParams.__name__ == 'MyOtherParams'
    assert MyOtherParams.my_int_or_float == 456
    assert MyOtherParams.my_str_or_none is None
    assert MyOtherParams.my_model is MyPydanticModel

    class MyOtherPydanticModel(BaseModel):
        x: str
        y: int

    MyThirdParams = MyParams.copy_and_adjust(
        'MyThirdParams',
        my_int_or_float=456.3,
        my_str_or_none=789,
        my_model=MyOtherPydanticModel,
    )
    assert MyThirdParams.__name__ == 'MyThirdParams'
    assert MyThirdParams.my_int_or_float == 456.3
    assert MyThirdParams.my_str_or_none == '789'
    assert MyThirdParams.my_model is MyOtherPydanticModel
    assert MyParams.my_model == MyPydanticModel

    with pytest.raises(ValidationError):
        MyParams.copy_and_adjust('MyFailingParams', my_int_or_float='abc', my_str_or_none='abc')

    with pytest.raises(TypeError):
        MyParams.copy_and_adjust('MyFailingParams', 456)  # type: ignore[call-arg]
