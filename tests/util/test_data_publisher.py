from typing import Annotated, Callable

import pytest

from .helpers.mocks import (MockAttrSubscriberCls,
                            MockConfigSubscriberCls,
                            MockDataPublisher,
                            MockDataPublisherGrandParent,
                            MockDataPublisherParent,
                            MockFoo,
                            MockParentConfigSubscriberCls)


def test_subscribe_attr_defaults(
    text_list: Annotated[list[str], pytest.fixture],
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> None:

    config = MockDataPublisher()

    assert config.foo is None
    assert config.text == 'bar'
    assert config.number == 42

    assert attr_subscriber.foo is None
    assert attr_subscriber.text == ''
    assert text_list == []

    config.subscribe_attr('foo', attr_subscriber.set_foo)
    config.subscribe_attr('text', list_appender_subscriber_func)
    config.subscribe_attr('text', attr_subscriber.set_text)

    assert attr_subscriber.foo is None
    assert attr_subscriber.text == 'bar'
    assert text_list == ['bar']


def test_subscribe_attr_init_values(
    text_list: Annotated[list[str], pytest.fixture],
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> None:

    foo = MockFoo()
    config = MockDataPublisher(foo=foo, text='foobar', number=0)

    assert config.foo is foo
    assert config.text == 'foobar'
    assert config.number == 0

    assert attr_subscriber.foo is None
    assert attr_subscriber.text == ''
    assert text_list == []

    config.subscribe_attr('foo', attr_subscriber.set_foo)
    config.subscribe_attr('text', list_appender_subscriber_func)
    config.subscribe_attr('text', attr_subscriber.set_text)

    assert attr_subscriber.foo is foo
    assert attr_subscriber.text == 'foobar'
    assert text_list == ['foobar']


def test_fail_subscribe_attr_incorrect_config_item(
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    mock_config_publisher_with_attr_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_attr_subscribers

    with pytest.raises(AttributeError):
        config.subscribe_attr('bar', attr_subscriber.set_foo)


def test_fail_subscribe_attr_private_config_item(
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    mock_config_publisher_with_attr_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_attr_subscribers

    with pytest.raises(AttributeError):
        config.subscribe_attr('_subscriptions', attr_subscriber.set_foo)


def test_subscribe_attr_setattr_no_subscribers(
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    mock_config_publisher_with_attr_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_attr_subscribers

    config.number = 5

    assert attr_subscriber.number == 10


def test_subscribe_attr_setattr_single_subscriber(
    text_list: Annotated[list[str], pytest.fixture],
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    mock_config_publisher_with_attr_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_attr_subscribers

    other_foo = MockFoo()
    attr_subscriber.set_foo(other_foo)

    foo = MockFoo()
    config.foo = foo

    assert attr_subscriber.foo is config.foo is foo

    foobar = MockFoo()
    config.foo = foobar

    assert attr_subscriber.foo is config.foo is foobar


def test_subscribe_attr_setattr_two_subscribers(
    text_list: Annotated[list[str], pytest.fixture],
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    mock_config_publisher_with_attr_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_attr_subscribers

    attr_subscriber.text = 'other'
    text_list.append('other')
    config.text = 'foobar'

    assert attr_subscriber.text == 'foobar'
    assert text_list == ['bar', 'other', 'foobar']

    config.text = ''

    assert attr_subscriber.text == ''
    assert text_list == ['bar', 'other', 'foobar', '']

    assert attr_subscriber.foo is config.foo is None


def test_subscribe_defaults(
        config_subscriber: Annotated[MockConfigSubscriberCls, pytest.fixture]) -> None:

    config = MockDataPublisher()

    assert config_subscriber.config is not config

    config.subscribe(config_subscriber.set_config)

    assert config_subscriber.config is config
    assert config_subscriber.config.foo is None
    assert config_subscriber.config.text == 'bar'


def test_subscribe_init_values(
        config_subscriber: Annotated[MockConfigSubscriberCls, pytest.fixture]) -> None:

    foo = MockFoo()
    config = MockDataPublisher(foo=foo, text='foobar', number=0)

    assert config_subscriber.config is not config

    config.subscribe(config_subscriber.set_config)

    assert config_subscriber.config is config
    assert config_subscriber.config.foo is foo
    assert config_subscriber.config.text == 'foobar'


def test_subscribe_setattr_with_subscriber(
        config_subscriber: Annotated[MockConfigSubscriberCls, pytest.fixture]) -> None:

    config = MockDataPublisher()
    config.subscribe(config_subscriber.set_config)

    other_foo = MockFoo()
    config_subscriber.config = MockDataPublisher(foo=other_foo, text='foobar', number=0)

    foo = MockFoo()
    config.foo = foo

    assert config_subscriber.config.foo is config.foo is foo

    foobar = MockFoo()
    config.foo = foobar

    assert config_subscriber.config.foo is config.foo is foobar


def test_parent_subscribe_attr_defaults(
        config_subscriber: Annotated[MockConfigSubscriberCls, pytest.fixture]) -> None:

    parent = MockDataPublisherParent()

    assert config_subscriber.config.foo is None
    assert config_subscriber.config.text == ''

    parent.subscribe_attr('config', config_subscriber.set_config)

    assert config_subscriber.config is parent.config

    assert config_subscriber.config.foo is None
    assert config_subscriber.config.text == 'bar'


def test_parent_subscribe_attr_with_subscriber(
        config_subscriber: Annotated[MockConfigSubscriberCls, pytest.fixture]) -> None:

    parent = MockDataPublisherParent()
    parent.subscribe_attr('config', config_subscriber.set_config)

    other_foo = MockFoo()
    config_subscriber.config = MockDataPublisher(foo=other_foo, text='foobar', number=0)

    foo = MockFoo()
    parent.config.foo = foo

    assert config_subscriber.config.foo is parent.config.foo is foo

    foobar = MockFoo()
    parent.config.foo = foobar

    assert config_subscriber.config.foo is parent.config.foo is foobar


def test_nested_parent_subscribe_attr_defaults(
        parent_config_subscriber: Annotated[MockParentConfigSubscriberCls, pytest.fixture]) -> None:

    grandparent = MockDataPublisherGrandParent()

    assert parent_config_subscriber.parent_config is not grandparent.parent_config

    assert parent_config_subscriber.parent_config.config.foo is None
    assert parent_config_subscriber.parent_config.config.text == ''

    grandparent.subscribe_attr('parent_config', parent_config_subscriber.set_parent_config)

    assert parent_config_subscriber.parent_config is grandparent.parent_config

    assert parent_config_subscriber.parent_config.config.foo is None
    assert parent_config_subscriber.parent_config.config.text == 'bar'


def test_nested_parent_subscribe_attr_with_subscriber(
        parent_config_subscriber: Annotated[MockParentConfigSubscriberCls, pytest.fixture]) -> None:

    grandparent = MockDataPublisherGrandParent()
    grandparent.subscribe_attr('parent_config', parent_config_subscriber.set_parent_config)

    parent_config_subscriber.parent_config = MockDataPublisherParent()
    other_foo = MockFoo()
    parent_config_subscriber.parent_config.config = MockDataPublisher(
        foo=other_foo, text='foobar', number=0)

    foo = MockFoo()
    grandparent.parent_config.config.foo = foo

    assert parent_config_subscriber.parent_config.config.foo \
           is grandparent.parent_config.config.foo is foo

    foobar = MockFoo()
    grandparent.parent_config.config.foo = foobar

    assert parent_config_subscriber.parent_config.config.foo \
           is grandparent.parent_config.config.foo is foobar


def test_unsubscribe_all(
    text_list: Annotated[list[str], pytest.fixture],
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    config_subscriber: Annotated[MockConfigSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
) -> None:

    config = MockDataPublisher()

    config.subscribe_attr('foo', attr_subscriber.set_foo)
    config.subscribe_attr('text', list_appender_subscriber_func)
    config.subscribe_attr('text', attr_subscriber.set_text)
    config.subscribe(config_subscriber.set_config)

    config.unsubscribe_all()

    config_subscriber.config = MockDataPublisher()
    config.foo = MockFoo()
    config.text = 'foobar'

    assert attr_subscriber.foo is None
    assert attr_subscriber.text == 'bar'
    assert text_list == ['bar']

    assert config_subscriber.config.foo is None


def test_change_subscribers_revert(
    text_list: Annotated[list[str], pytest.fixture],
    attr_subscriber: Annotated[MockAttrSubscriberCls, pytest.fixture],
    list_appender_subscriber_func: Annotated[Callable[[str], None], pytest.fixture],
    mock_config_publisher_with_attr_subscribers: Annotated[MockDataPublisher, pytest.fixture],
) -> None:

    config = mock_config_publisher_with_attr_subscribers

    foo = MockFoo()
    attr_subscriber.set_foo(foo)
    list_appender_subscriber_func('foobar')

    assert attr_subscriber.foo is foo
    assert attr_subscriber.text == 'bar'
    assert text_list == ['bar', 'foobar']
    assert config.foo is None
    assert config.text == 'bar'

    config.foo = config.foo
    config.text = config.text

    assert attr_subscriber.foo is None
    assert attr_subscriber.text == 'bar'
    assert text_list == ['bar', 'foobar', 'bar']
