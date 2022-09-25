import pytest

from unifair.compute.job import JobCreator


def test_job_creator_init():
    with pytest.raises(TypeError):
        JobCreator('something')  # noqa

    job_creator_1 = JobCreator()
    job_creator_2 = JobCreator()

    assert job_creator_1 != job_creator_2


def test_job_creator_set_engine(mock_engine):
    job_creator = JobCreator()

    assert job_creator.engine is None
    with pytest.raises(AttributeError):
        job_creator.engine = mock_engine  # noqa

    job_creator.set_engine(mock_engine)
    assert job_creator.engine == mock_engine


def test_job_creator_engine_not_singular(mock_engine):
    job_creator_1 = JobCreator()
    job_creator_2 = JobCreator()

    job_creator_1.set_engine(mock_engine)
    assert job_creator_2.engine is None
