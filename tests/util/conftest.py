"""Shared fixtures for utility tests."""

from typing import Annotated, Callable

import pytest

from .helpers.mocks import (MockAttrSubscriberCls,
                            MockConfigSubscriberCls,
                            MockDataPublisher,
                            MockParentConfigSubscriberCls)


@pytest.fixture(scope='function')
def attr_subscriber() -> MockAttrSubscriberCls:
    """Provide the attr subscriber fixture."""
    return MockAttrSubscriberCls()


@pytest.fixture(scope='function')
def config_subscriber() -> MockConfigSubscriberCls:
    """Provide the configuration subscriber fixture."""
    return MockConfigSubscriberCls()


@pytest.fixture(scope='function')
def parent_config_subscriber() -> MockParentConfigSubscriberCls:
    """Provide the parent configuration subscriber fixture."""
    return MockParentConfigSubscriberCls()


@pytest.fixture(scope='function')
def text_list() -> list[str]:
    """Provide the text list fixture."""
    return []


@pytest.fixture(scope='function')
def list_appender_subscriber_func(
        text_list: Annotated[list[str], pytest.fixture]) -> Callable[[str], None]:
    """Provide the list appender subscriber func fixture."""
    def list_appender_subscriber_func(text: str) -> None:
        text_list.append(text)

    return list_appender_subscriber_func


@pytest.fixture(scope='function')
def mock_config_publisher_with_attr_subscribers(
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> MockDataPublisher:
    """Provide the mock configuration publisher with attr subscribers fixture."""
    config = MockDataPublisher()

    config.subscribe_attr('foo', attr_subscriber.set_foo)
    config.subscribe_attr('text', list_appender_subscriber_func)
    config.subscribe_attr('text', attr_subscriber.set_text)

    return config
