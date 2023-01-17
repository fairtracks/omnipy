import logging
from typing import Annotated, Callable, List

import pytest

from .helpers.mocks import MockConfigPublisher, MockSubscriberCls


@pytest.fixture(scope='function')
def subscriber_obj() -> MockSubscriberCls:
    return MockSubscriberCls()


@pytest.fixture(scope='function')
def text_list() -> List[str]:
    return []


@pytest.fixture(scope='function')
def list_appender_subscriber_func(
        text_list: Annotated[List[str], pytest.fixture]) -> Callable[[str], None]:
    def list_appender_subscriber_func(text: str) -> None:
        text_list.append(text)

    return list_appender_subscriber_func


@pytest.fixture(scope='function')
def mock_config_publisher_with_subscribers(
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> MockConfigPublisher:

    config = MockConfigPublisher()

    config.subscribe('foo', subscriber_obj.set_foo)
    config.subscribe('text', list_appender_subscriber_func)
    config.subscribe('text', subscriber_obj.set_text)

    return config


@pytest.fixture(scope='module')
def teardown_loggers():
    yield
    logger = logging.getLogger('omnipy')
    for handler in logger.handlers:
        logger.removeHandler(handler)
