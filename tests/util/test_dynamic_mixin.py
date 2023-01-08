from abc import ABCMeta
from inspect import Parameter, signature
from typing import Dict, Tuple, Type

import pytest

from unifair.util.mixin import DynamicMixinAcceptor, DynamicMixinAcceptorFactory


@pytest.fixture(scope='function')
def mock_plain_cls() -> Type:
    class MockPlainCls(DynamicMixinAcceptor):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def to_override(self):
            return self.__class__.__name__

    return MockPlainCls


@pytest.fixture(scope='function')
def mock_other_plain_cls() -> Type:
    class MockOtherPlainCls(DynamicMixinAcceptor):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def to_override(self):
            return self.__class__.__name__

    return MockOtherPlainCls


def test_no_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert not hasattr(mock_plain_obj, 'new_method')
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


def _assert_args_and_kwargs(MockPlainCls: Type[DynamicMixinAcceptor],
                            mock_plain_obj: DynamicMixinAcceptor,
                            args: Tuple[object, ...],
                            kwargs: Dict[str, object],
                            mixin_init_kwarg_params: Dict[str, Parameter] = {}):

    assert tuple(signature(MockPlainCls.__init__).parameters.keys()) == tuple(
        ['self', 'args'] + list(mixin_init_kwarg_params.keys()) + ['kwargs'],)
    assert tuple(signature(mock_plain_obj.__init__).parameters.keys()) == tuple(
        ['args'] + list(mixin_init_kwarg_params.keys()) + ['kwargs'],)

    assert mock_plain_obj._mixin_init_kwarg_params == mixin_init_kwarg_params
    assert mock_plain_obj.args == args
    assert mock_plain_obj.kwargs == kwargs


class MockNewMethodNoStateMixin:
    @classmethod
    def new_method(cls):
        return 'new method'


def test_new_method_no_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


class MockOtherNewMethodNoStateMixin:
    @classmethod
    def new_method(cls):
        return 'other new method'


def test_multiple_new_method_no_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)
    MockPlainCls.accept_mixin(MockOtherNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'other new method'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


class MockOverrideNoStateMixin:
    # @classmethod
    def to_override(self):
        return 'overridden method'


def test_override_no_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert not hasattr(mock_plain_obj, 'new_method')
    assert mock_plain_obj.to_override() == 'overridden method'


def test_progressive_multiple_new_method_and_override_no_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'

    MockPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.to_override() == 'overridden method'


def test_multiple_orig_class_different_no_state_mixins(mock_plain_cls, mock_other_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'

    MockOtherPlainCls = mock_other_plain_cls  # noqa
    MockOtherPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_other_plain_obj = MockOtherPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        MockOtherPlainCls, mock_other_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert not hasattr(mock_other_plain_obj, 'new_method')
    assert mock_other_plain_obj.to_override() == 'overridden method'


class MockKwArgStateDependentMixin:
    def __init__(self, *, my_kwarg_1, my_kwarg_2='default value'):
        self._my_kwarg_1 = my_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return self._my_kwarg_1

    def to_override(self):
        return self._my_kwarg_2


def test_state_dependent_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateDependentMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')))

    assert mock_plain_obj.new_method() == 'value'
    assert mock_plain_obj.to_override() == 'default value'


class MockOtherKwArgStateDependentMixin:
    def __init__(self, *, my_other_kwarg_1, my_kwarg_2='other default value'):
        self._my_other_kwarg_1 = my_other_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return self._my_other_kwarg_1

    def to_override(self):
        return self._my_kwarg_2


def test_fail_missing_kwargs_multiple_state_dependent_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateDependentMixin)
    MockPlainCls.accept_mixin(MockOtherKwArgStateDependentMixin)

    with pytest.raises(TypeError):
        MockPlainCls('a', 1, verbose=True)

    with pytest.raises(TypeError):
        MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    with pytest.raises(TypeError):
        MockPlainCls('a', 1, verbose=True, my_other_kwarg_1='other value')


def test_progressive_multiple_state_dependent_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockKwArgStateDependentMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')))

    assert mock_plain_obj.new_method() == 'value'
    assert mock_plain_obj.to_override() == 'default value'

    MockPlainCls.accept_mixin(MockOtherKwArgStateDependentMixin)

    mock_plain_obj = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(
            verbose=True,
            my_kwarg_1='value',
            my_kwarg_2='other default value',
            my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter(
                'my_kwarg_2', Parameter.KEYWORD_ONLY, default='other default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)))

    assert mock_plain_obj.new_method() == 'other value'
    assert mock_plain_obj.to_override() == 'other default value'

    mock_plain_obj = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter(
                'my_kwarg_2', Parameter.KEYWORD_ONLY, default='other default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)))

    assert mock_plain_obj.new_method() == 'alt1B'
    assert mock_plain_obj.to_override() == 'alt2'


def test_multiple_orig_class_different_state_dependent_mixins(mock_plain_cls, mock_other_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateDependentMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')))

    assert mock_plain_obj.new_method() == 'value'
    assert mock_plain_obj.to_override() == 'default value'

    MockOtherPlainCls = mock_other_plain_cls  # noqa
    MockOtherPlainCls.accept_mixin(MockOtherKwArgStateDependentMixin)

    mock_other_plain_obj = MockOtherPlainCls('a', 1, verbose=True, my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        MockOtherPlainCls,
        mock_other_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_2='other default value', my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter(
                'my_kwarg_2', Parameter.KEYWORD_ONLY, default='other default value')))

    assert mock_other_plain_obj.new_method() == 'other value'
    assert mock_other_plain_obj.to_override() == 'other default value'


def test_fail_no_init_method_state_dependent_mixin():
    with pytest.raises(TypeError):

        class MockNoInitCls(DynamicMixinAcceptor):
            def to_override(self):
                return self.__class__.__name__


def test_fail_missing_kwargs_init_param_state_dependent_mixin():
    class MockNoKwargInitCls(DynamicMixinAcceptor):
        def __init__(self, *args):
            self.args = args
            self.kwargs = {}

        def to_override(self):
            return self.__class__.__name__

    with pytest.raises(AttributeError):
        MockNoKwargInitCls.accept_mixin(MockKwArgStateDependentMixin)


class MockPosOnlyArgStateDependentMixin:
    def __init__(self, my_pos_only_arg, /):
        self._my_pos_only_arg = my_pos_only_arg


def test_fail_pos_only_arg_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    with pytest.raises(AttributeError):
        MockPlainCls.accept_mixin(MockPosOnlyArgStateDependentMixin)


def test_predefined_init_kwargs_progressive_multiple_state_dependent_mixins():
    class MockPredefinedInitKwargsCls(DynamicMixinAcceptor):
        def __init__(self, *args, my_kwarg_1, my_kwarg_2='my default value', **kwargs):
            kwargs.update({'my_kwarg_1': my_kwarg_1, 'my_kwarg_2': my_kwarg_2})
            self.args = args
            self.kwargs = kwargs

        def to_override(self):
            return self.__class__.__name__

    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateDependentMixin)

    mock_predefined_init_kwargs_plain_obj = MockPredefinedInitKwargsCls(
        'a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        MockPredefinedInitKwargsCls,
        mock_predefined_init_kwargs_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')))

    assert mock_predefined_init_kwargs_plain_obj.new_method() == 'value'
    assert mock_predefined_init_kwargs_plain_obj.to_override() == 'default value'

    MockPredefinedInitKwargsCls.accept_mixin(MockOtherKwArgStateDependentMixin)

    mock_predefined_init_kwargs_plain_obj = MockPredefinedInitKwargsCls(
        'a', 1, verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        MockPredefinedInitKwargsCls,
        mock_predefined_init_kwargs_plain_obj,
        args=('a', 1),
        kwargs=dict(
            verbose=True,
            my_kwarg_1='value',
            my_kwarg_2='other default value',
            my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter(
                'my_kwarg_2', Parameter.KEYWORD_ONLY, default='other default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)))

    assert mock_predefined_init_kwargs_plain_obj.new_method() == 'other value'
    assert mock_predefined_init_kwargs_plain_obj.to_override() == 'other default value'


def test_other_metaclass_for_base_cls_state_dependent_mixin():
    class OtherMetaClass(ABCMeta):
        def __new__(mcs, name, bases, namespace):
            cls = super().__new__(mcs, name, bases, namespace)
            cls._member = 'something'
            return cls

    class OtherBase(metaclass=OtherMetaClass):
        ...

    class MergedMetaClass(OtherMetaClass, DynamicMixinAcceptorFactory):
        ...

    class MockOtherMetaclassForBaseCls(OtherBase, DynamicMixinAcceptor, metaclass=MergedMetaClass):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def to_override(self):
            return self.__class__.__name__

    MockOtherMetaclassForBaseCls.accept_mixin(MockKwArgStateDependentMixin)

    mock_other_metaclass_for_base_obj = MockOtherMetaclassForBaseCls(
        'a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        MockOtherMetaclassForBaseCls,
        mock_other_metaclass_for_base_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')))

    assert mock_other_metaclass_for_base_obj.new_method() == 'value'
    assert mock_other_metaclass_for_base_obj.to_override() == 'default value'
    assert mock_other_metaclass_for_base_obj._member == 'something'
