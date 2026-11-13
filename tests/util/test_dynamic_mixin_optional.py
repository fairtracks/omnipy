"""Tests for optional mixins, unclaimed keyword arguments and mixin registration by class."""

from typing import Any

from omnipy.util.mixin import DynamicMixinAcceptor, RECEIVES_UNCLAIMED_KWARGS_ATTR


def _make_acceptor_cls() -> Any:
    class Acceptor(DynamicMixinAcceptor):
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args

    return Acceptor


class OptionMixin:
    def __init__(self, *, option: str = 'default') -> None:
        self.option = option


class ReceiverMixin:
    def __init__(self, **kwargs: object) -> None:
        self.unclaimed = kwargs


setattr(ReceiverMixin, RECEIVES_UNCLAIMED_KWARGS_ATTR, True)


def _make_same_named_mixins() -> tuple[type, type]:
    class SameName:
        def __init__(self, *, first: int = 1) -> None:
            self.first = first

    first_cls = SameName

    class SameName:  # type: ignore[no-redef]
        def __init__(self, *, second: int = 2) -> None:
            self.second = second

    return first_cls, SameName


def test_optional_mixin_activated_by_non_default_keyword() -> None:
    acceptor_cls = _make_acceptor_cls()
    acceptor_cls.accept_mixin(OptionMixin, optional=True)

    assert not hasattr(acceptor_cls(), 'option')
    assert not hasattr(acceptor_cls(option='default'), 'option')
    assert acceptor_cls(option='set').option == 'set'


def test_optional_mixin_activated_by_function() -> None:
    acceptor_cls = _make_acceptor_cls()
    state = {'active': False}
    acceptor_cls.accept_mixin(OptionMixin, optional=True, activate_if=lambda: state['active'])

    assert not hasattr(acceptor_cls(), 'option')
    state['active'] = True
    assert acceptor_cls().option == 'default'


def test_unclaimed_keywords_go_to_receiver_mixin() -> None:
    acceptor_cls = _make_acceptor_cls()
    acceptor_cls.accept_mixin(OptionMixin)
    acceptor_cls.accept_mixin(ReceiverMixin)

    obj = acceptor_cls('a', option='set', other=1)

    assert obj.args == ('a',)
    assert obj.option == 'set'
    assert obj.unclaimed == {'other': 1}


def test_keywords_of_inactive_optional_mixins_are_not_unclaimed() -> None:
    acceptor_cls = _make_acceptor_cls()
    acceptor_cls.accept_mixin(OptionMixin, optional=True)
    acceptor_cls.accept_mixin(ReceiverMixin)

    obj = acceptor_cls(option='default')

    assert not hasattr(obj, 'option')
    assert obj.unclaimed == {}


def test_mixins_with_the_same_class_name_are_registered_separately() -> None:
    first_cls, second_cls = _make_same_named_mixins()
    acceptor_cls = _make_acceptor_cls()
    acceptor_cls.accept_mixin(first_cls, optional=True)
    acceptor_cls.accept_mixin(second_cls)

    # With registration by class name, the keywords of both mixins were stored under one entry,
    # so giving "second" would also activate the optional first mixin
    obj = acceptor_cls(second=20)

    assert not hasattr(obj, 'first')
    assert obj.second == 20
    assert acceptor_cls(first=10).first == 10
