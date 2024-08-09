import pytest

from engine.helpers.mocks import (MockDagFlow,
                                  MockDagFlowTemplate,
                                  MockJobRunnerSubclass,
                                  MockTask,
                                  MockTaskTemplate)


@pytest.fixture(scope='module')
def task_template_a() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='a')
    def concat_a(s: str) -> str:
        return s + 'a'

    return concat_a


@pytest.fixture(scope='module')
def task_template_b() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='b')
    def concat_b(s: str) -> str:
        return s + 'b'

    return concat_b


@pytest.fixture(scope='module')
def task_a(task_template_a) -> MockTask:
    return task_template_a.apply()


@pytest.fixture(scope='module')
def task_b(task_template_b) -> MockTask:
    return task_template_b.apply()


@pytest.fixture(scope='module')
def dag_flow_a(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='a')
    def concat_a(s: str) -> str:
        ...

    return concat_a.apply()


@pytest.fixture(scope='module')
def dag_flow_b(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='b')
    def concat_b(s: str) -> str:
        ...

    return concat_b.apply()
