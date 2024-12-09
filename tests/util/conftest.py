from typing import Annotated, Callable

import pytest

from .helpers.mocks import (MockAttrSubscriberCls,
                            MockConfigSubscriberCls,
                            MockDataPublisher,
                            MockParentConfigSubscriberCls)


@pytest.fixture(scope='function')
def attr_subscriber() -> MockAttrSubscriberCls:
    return MockAttrSubscriberCls()


@pytest.fixture(scope='function')
def config_subscriber() -> MockConfigSubscriberCls:
    return MockConfigSubscriberCls()


@pytest.fixture(scope='function')
def parent_config_subscriber() -> MockParentConfigSubscriberCls:
    return MockParentConfigSubscriberCls()


@pytest.fixture(scope='function')
def text_list() -> list[str]:
    return []


@pytest.fixture(scope='function')
def list_appender_subscriber_func(
        text_list: Annotated[list[str], pytest.fixture]) -> Callable[[str], None]:
    def list_appender_subscriber_func(text: str) -> None:
        text_list.append(text)

    return list_appender_subscriber_func


@pytest.fixture(scope='function')
def mock_config_publisher_with_attr_subscribers(
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> MockDataPublisher:

    config = MockDataPublisher()

    config.subscribe_attr('foo', attr_subscriber.set_foo)
    config.subscribe_attr('text', list_appender_subscriber_func)
    config.subscribe_attr('text', attr_subscriber.set_text)

    return config
