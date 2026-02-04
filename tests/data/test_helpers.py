import pytest

from omnipy.data.helpers import FailedData, PendingData
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError


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
