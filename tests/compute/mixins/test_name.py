from typing import Annotated

import pytest

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate

from ..cases.raw.functions import power_m1_func
from ..conftest import MockJobClasses
from ..helpers.mocks import MockLocalRunner


def test_property_name_default_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes
    job_tmpl = JobTemplate()

    for job in job_tmpl, job_tmpl.apply():
        assert job.name is None

        with pytest.raises(AttributeError):
            job.name = 'cool_name'  # pyright: ignore [reportAttributeAccessIssue]


def test_property_name_default_task() -> None:

    power_m1_tmpl = TaskTemplate()(power_m1_func)

    for power_m1_obj in power_m1_tmpl, power_m1_tmpl.apply():
        assert power_m1_obj.name == 'power_m1_func'


def test_property_name_default_linear_flow(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:

    power_m1_tmpl = LinearFlowTemplate()(power_m1_func)

    for power_m1_obj in power_m1_tmpl, power_m1_tmpl.apply():
        assert power_m1_obj.name == 'power_m1_func'


def test_property_name_default_dag_flow(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:

    power_m1_tmpl = DagFlowTemplate()(power_m1_func)

    for power_m1_obj in power_m1_tmpl, power_m1_tmpl.apply():
        assert power_m1_obj.name == 'power_m1_func'


def test_property_name_default_func_flow(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:

    power_m1_tmpl = FuncFlowTemplate()(power_m1_func)

    for power_m1_obj in power_m1_tmpl, power_m1_tmpl.apply():
        assert power_m1_obj.name == 'power_m1_func'


def test_property_name_change_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job_tmpl = JobTemplate(name='my_job')

    for job in job_tmpl, job_tmpl.apply():
        assert job.name == 'my_job'

        with pytest.raises(AttributeError):
            job.name = 'my_cool_job'  # type: ignore[misc]


def test_property_name_validation_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job_tmpl = JobTemplate(name=None)
    assert job_tmpl.name is None

    with pytest.raises(ValueError):
        JobTemplate(name='')

    with pytest.raises(TypeError):
        JobTemplate(name=123)  # pyright: ignore [reportArgumentType]


def test_property_unique_name_default_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job_tmpl = JobTemplate()

    for job in job_tmpl, job_tmpl.apply():
        assert job.unique_name is None

        with pytest.raises(AttributeError):
            job.unique_name = 'cool_name'  # pyright: ignore [reportAttributeAccessIssue]


def test_property_unique_name_change_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job_tmpl = JobTemplate(name='my_job')
    assert job_tmpl.unique_name is None

    job = job_tmpl.apply()
    assert job_tmpl.unique_name is None

    assert job.unique_name.startswith('mock-job-subclass-my-job-')
    assert job.unique_name != job.name

    with pytest.raises(AttributeError):
        unique_name = 'mock-job-subclass-my-job-crouching-dolphin'
        job.unique_name = unique_name  # pyright: ignore [reportAttributeAccessIssue]


def test_property_unique_name_uniqueness_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job_tmpl = JobTemplate(name='my_job')

    job_1 = job_tmpl.apply()
    job_2 = job_tmpl.apply()

    assert job_1.unique_name.startswith('mock-job-subclass-my-job-')
    assert job_1.unique_name != job_1.name

    assert job_2.unique_name.startswith('mock-job-subclass-my-job-')
    assert job_2.unique_name != job_2.name

    assert job_1.name == job_2.name
    assert job_1.unique_name != job_2.unique_name


def test_property_unique_name_regenerate_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job = JobTemplate(name='my_job').apply()

    assert job.unique_name.startswith('mock-job-subclass-my-job-')
    assert job.unique_name != job.name

    prev_unique_name = job.unique_name
    job.regenerate_unique_name()

    assert job.unique_name.startswith('mock-job-subclass-my-job-')
    assert job.unique_name != job.name

    assert job.unique_name != prev_unique_name


def test_property_unique_name_revise_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    job = JobTemplate(name='my_job').apply()
    assert job.unique_name is not None

    new_job_tmpl = job.revise()
    assert new_job_tmpl.unique_name is None


def test_equal_job_dependent_on_name_mock(
        mock_job_classes: Annotated[MockJobClasses, pytest.fixture]) -> None:
    JobTemplate, _ = mock_job_classes

    my_job_tmpl = JobTemplate(name='my_job')
    my_job_tmpl_2 = JobTemplate(name='my_job')

    for (my_job_obj, my_job_obj_2) in [(my_job_tmpl, my_job_tmpl_2),
                                       (my_job_tmpl.apply(), my_job_tmpl_2.apply())]:
        assert my_job_obj == my_job_obj_2

    other_job_tmpl = JobTemplate(name='other_job')

    for (my_job_obj, other_job_obj) in [(my_job_tmpl, other_job_tmpl),
                                        (my_job_tmpl.apply(), other_job_tmpl.apply())]:
        assert my_job_obj != other_job_obj
