import pytest

from unifair.dataset.model import Model


@pytest.fixture
def StringToLength():  # noqa
    class StringToLength(Model[str]):
        @classmethod
        def _parse_data(cls, data: str) -> int:
            return len(data)

    return StringToLength
