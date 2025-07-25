from typing import Literal

import pytest

from omnipy.data.helpers import FailedData, PendingData
from omnipy.data.model import Model
from omnipy.data.typechecks import is_model_instance, obj_or_model_content_isinstance
from omnipy.util._pydantic import ValidationError

from .helpers.models import PydanticParentModel


def test_is_model_instance() -> None:
    assert not is_model_instance(123)
    assert is_model_instance(Model[int](123))
    assert not is_model_instance(None)
    assert is_model_instance(Model[None](None))
    assert not is_model_instance(PydanticParentModel)


def test_obj_or_model_content_isinstance_for_regular_objects() -> None:
    assert obj_or_model_content_isinstance(123, int)
    assert obj_or_model_content_isinstance('abc', str)
    assert obj_or_model_content_isinstance([1, 2, 3], list)

    assert not obj_or_model_content_isinstance(123, list)
    assert not obj_or_model_content_isinstance('abc', int)
    assert not obj_or_model_content_isinstance([1, 2, 3], str)

    assert obj_or_model_content_isinstance(123, (list, int))
    assert obj_or_model_content_isinstance('abc', (int, str))
    assert obj_or_model_content_isinstance([1, 2, 3], (str, list))

    assert obj_or_model_content_isinstance(123, list | int)
    assert obj_or_model_content_isinstance('abc', int | str)
    assert obj_or_model_content_isinstance([1, 2, 3], str | list)

    with pytest.raises(TypeError):
        obj_or_model_content_isinstance('abc', Literal['abc'])  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        obj_or_model_content_isinstance([1, 2, 3], list[int])


def test_obj_or_model_content_isinstance_for_models() -> None:
    assert obj_or_model_content_isinstance(Model[int](123), int)
    assert obj_or_model_content_isinstance(Model[str]('abc'), str)
    assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), list)

    assert not obj_or_model_content_isinstance(Model[int](123), list)
    assert not obj_or_model_content_isinstance(Model[str]('abc'), int)
    assert not obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), str)

    assert obj_or_model_content_isinstance(Model[int](123), (list, int))
    assert obj_or_model_content_isinstance(Model[str]('abc'), (int, str))
    assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), (str, list))

    assert obj_or_model_content_isinstance(Model[int](123), list | int)
    assert obj_or_model_content_isinstance(Model[str]('abc'), int | str)
    assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), str | list)

    with pytest.raises(TypeError):
        assert obj_or_model_content_isinstance(
            Model[Literal['abc']]('abc'),
            Literal['abc'],  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError):
        assert obj_or_model_content_isinstance(Model[list[int]]([1, 2, 3]), list[int])


# noinspection PyDataclass
def test_pending_data() -> None:
    with pytest.raises(TypeError):
        PendingData()  # type: ignore[call-arg]

    pending_data = PendingData(job_name='my_task', job_unique_name='my-task-nostalgic-labradoodle')
    assert pending_data.job_name == 'my_task'
    assert pending_data.job_unique_name == 'my-task-nostalgic-labradoodle'

    with pytest.raises(AttributeError):
        pending_data.job_name = 'my_other_task'  # type: ignore[misc]
        pending_data.job_unique_name = 'my-task-nostalgic-poodle'  # type: ignore[misc]

    with pytest.raises(ValidationError):
        Model[str](pending_data)


# noinspection PyDataclass
def test_failed_data() -> None:
    with pytest.raises(TypeError):
        FailedData()  # type: ignore[call-arg]

    exception = RuntimeError('Some error')
    error_data = FailedData(
        job_name='my_task',
        job_unique_name='my-task-nostalgic-poodle',
        exception=exception,
    )
    assert error_data.job_name == 'my_task'
    assert error_data.job_unique_name == 'my-task-nostalgic-poodle'
    assert error_data.exception is exception

    with pytest.raises(AttributeError):
        error_data.job_name = 'my_other_task'  # type: ignore[misc]
        error_data.job_unique_name = 'my-other-task-nostalgic-labradoodle'  # type: ignore[misc]
        error_data.exception = Exception('other errors')  # type: ignore[misc]

    with pytest.raises(ValidationError):
        Model[str](error_data)
