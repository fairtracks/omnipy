import pytest

from compute.helpers.mocks import MockJobConfig, MockLocalRunner
from omnipy.compute.job import JobCreator


def test_job_creator_init():
    with pytest.raises(TypeError):
        JobCreator('something')  # noqa

    job_creator_1 = JobCreator()
    job_creator_2 = JobCreator()

    assert job_creator_1 != job_creator_2


def test_job_creator_set_engine():
    mock_local_runner = MockLocalRunner()
    job_creator = JobCreator()

    assert job_creator.engine is None
    with pytest.raises(AttributeError):
        job_creator.engine = mock_local_runner  # noqa

    job_creator.set_engine(mock_local_runner)
    assert job_creator.engine == mock_local_runner


def test_job_creator_set_config():
    mock_job_config = MockJobConfig()
    job_creator = JobCreator()

    assert job_creator.config is None
    with pytest.raises(AttributeError):
        job_creator.config = mock_job_config  # noqa

    job_creator.set_config(mock_job_config)
    assert job_creator.config == mock_job_config


def test_job_creator_engine_not_singular():
    mock_local_runner = MockLocalRunner()
    mock_job_config = MockJobConfig()

    job_creator_1 = JobCreator()
    job_creator_2 = JobCreator()

    job_creator_1.set_engine(mock_local_runner)
    assert job_creator_2.engine is None

    job_creator_1.set_config(mock_job_config)
    assert job_creator_2.config is None


def test_job_creator_nested_context_level():
    job_creator = JobCreator()

    assert job_creator.nested_context_level == 0

    try:
        with job_creator:
            assert job_creator.nested_context_level == 1

            with job_creator:
                assert job_creator.nested_context_level == 2

            assert job_creator.nested_context_level == 1
            raise RuntimeError()
    except RuntimeError:
        pass

    assert job_creator.nested_context_level == 0
