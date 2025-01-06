import pytest

from omnipy.compute._job_creator import JobCreator
from omnipy.config.job import JobConfig

from .helpers.mocks import MockJobConfig, MockLocalRunner


def test_job_creator_init() -> None:
    with pytest.raises(TypeError):
        JobCreator('something')  # type: ignore[call-arg]

    job_creator_1 = JobCreator()
    job_creator_2 = JobCreator()

    assert job_creator_1 != job_creator_2


def test_job_creator_set_engine() -> None:
    mock_local_runner = MockLocalRunner()
    job_creator = JobCreator()

    assert job_creator.engine is None
    with pytest.raises(AttributeError):
        job_creator.engine = mock_local_runner  # type: ignore[misc]

    job_creator.set_engine(mock_local_runner)
    assert job_creator.engine == mock_local_runner


def test_job_creator_set_config() -> None:
    mock_job_config = MockJobConfig()
    job_creator = JobCreator()

    assert isinstance(job_creator.config, JobConfig)
    with pytest.raises(AttributeError):
        job_creator.config = mock_job_config  # type: ignore[misc, assignment]

    job_creator.set_config(mock_job_config)  # type: ignore[arg-type]
    assert job_creator.config == mock_job_config


def test_job_creator_engine_not_singular() -> None:
    mock_local_runner = MockLocalRunner()
    mock_job_config = MockJobConfig()

    job_creator_1 = JobCreator()
    job_creator_2 = JobCreator()

    job_creator_1.set_engine(mock_local_runner)
    assert job_creator_2.engine is None

    job_creator_1.set_config(mock_job_config)  # type: ignore[arg-type]
    assert isinstance(job_creator_2.config, JobConfig)


def test_job_creator_nested_context_level() -> None:
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
