from typing import Annotated, Callable

import pytest

from .helpers.mocks import MockDataPublisher, MockFoo, MockSubscriberCls


def test_init_default() -> None:
    config = MockDataPublisher()
    assert config.foo is None
    assert config.text == 'bar'
    assert config.number == 42


def test_init_params() -> None:
    foo = MockFoo()
    config = MockDataPublisher(foo=foo, text='foobar', number=1)
    assert config.foo is foo
    assert config.text == 'foobar'
    assert config.number == 1


def test_unregistered_subscribers(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> None:

    assert subscriber_obj.foo is None
    assert subscriber_obj.text == ''
    assert text_list == []


def test_subscribe_defaults(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> None:

    config = MockDataPublisher()

    config.subscribe('foo', subscriber_obj.set_foo)
    config.subscribe('text', list_appender_subscriber_func)
    config.subscribe('text', subscriber_obj.set_text)

    assert subscriber_obj.foo is None
    assert subscriber_obj.text == 'bar'
    assert text_list == ['bar']


def test_subscribe_init_values(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> None:

    foo = MockFoo()
    config = MockDataPublisher(foo=foo, text='foobar', number=0)

    config.subscribe('foo', subscriber_obj.set_foo)
    config.subscribe('text', list_appender_subscriber_func)
    config.subscribe('text', subscriber_obj.set_text)

    assert subscriber_obj.foo is foo
    assert subscriber_obj.text == 'foobar'
    assert text_list == ['foobar']


def test_fail_subscribe_incorrect_config_item(
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    with pytest.raises(AttributeError):
        config.subscribe('bar', subscriber_obj.set_foo)


def test_fail_subscribe_private_config_item(
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    with pytest.raises(AttributeError):
        config.subscribe('_subscriptions', subscriber_obj.set_foo)


def test_setattr_no_subscribers(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    config.number = 0

    assert subscriber_obj.foo is None
    assert subscriber_obj.text == 'bar'
    assert text_list == ['bar']


def test_setattr_single_subscriber(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    foo = MockFoo()
    config.foo = foo

    assert subscriber_obj.foo is config.foo is foo

    foobar = MockFoo()
    config.foo = foobar

    assert subscriber_obj.foo is config.foo is foobar

    assert subscriber_obj.text == 'bar'
    assert text_list == ['bar']


def test_setattr_two_subscribers(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    config.text = 'foobar'

    assert subscriber_obj.text == 'foobar'
    assert text_list == ['bar', 'foobar']

    config.text = ''

    assert subscriber_obj.text == ''
    assert text_list == ['bar', 'foobar', '']

    assert subscriber_obj.foo is config.foo is None


def test_unsubscribe_all(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    config.unsubscribe_all()
    config.foo = MockFoo()
    config.text = 'foobar'

    assert subscriber_obj.foo is None
    assert subscriber_obj.text == 'bar'
    assert text_list == ['bar']


def test_change_subscribers_no_effect(
    text_list: Annotated[list[str], pytest.fixture],
    subscriber_obj: Annotated[MockSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
    mock_config_publisher_with_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_subscribers

    foo = MockFoo()
    subscriber_obj.set_foo(foo)
    list_appender_subscriber_func('foobar')

    assert subscriber_obj.foo is foo
    assert subscriber_obj.text == 'bar'
    assert text_list == ['bar', 'foobar']
    assert config.foo is None
    assert config.text == 'bar'

    config.foo = config.foo
    config.text = config.text

    assert subscriber_obj.foo is None
    assert subscriber_obj.text == 'bar'
    assert text_list == ['bar', 'foobar', 'bar']
