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


class MockNewMethodNoStateMixin:
    @classmethod
    def new_method(cls):
        return 'new method'


class MockOtherNewMethodNoStateMixin:
    @classmethod
    def new_method(cls):
        return 'other new method'


class MockOverrideNoStateMixin:
    # @classmethod
    def to_override(self):
        return 'overridden method'


class MockKwArgStateMixin:
    def __init__(self, *, my_kwarg_1, my_kwarg_2='default value'):
        self._my_kwarg_1 = my_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return self._my_kwarg_1

    def to_override(self):
        return self._my_kwarg_2


class MockOtherKwArgStateMixin:
    def __init__(self, *, my_other_kwarg_1, my_kwarg_2='default value'):
        self._my_other_kwarg_1 = my_other_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return self._my_other_kwarg_1

    def to_override(self):
        return self._my_kwarg_2


class MockKwArgAccessOrigClsMemberStateMixin:
    def __init__(self, *, my_kwarg):
        self._value = f'my_kwarg: {my_kwarg}' if self.kwargs.get('verbose') == True else my_kwarg

    def new_method(self):
        return self._value


class MockOtherKwArgDiffDefaultStateMixin:
    def __init__(self, *, my_other_kwarg_1, my_kwarg_2='other default value'):
        self._my_other_kwarg_1 = my_other_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return self._my_other_kwarg_1

    def to_override(self):
        return self._my_kwarg_2


class MockPosOnlyArgStateMixin:
    def __init__(self, my_pos_only_arg, /):
        self._my_pos_only_arg = my_pos_only_arg


@pytest.fixture(scope='function')
def mock_predefined_init_kwargs_cls() -> Type:
    class MockPredefinedInitKwargsCls(DynamicMixinAcceptor):
        def __init__(self, *args, my_kwarg_1, my_kwarg_2='default value', **kwargs):
            kwargs.update({'my_kwarg_1': my_kwarg_1, 'my_kwarg_2': my_kwarg_2})
            self.args = args
            self.kwargs = kwargs

        def to_override(self):
            return self.__class__.__name__

    return MockPredefinedInitKwargsCls


def test_no_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert not hasattr(mock_plain_obj, 'new_method')
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


def _assert_args_and_kwargs(MockCls: Type[DynamicMixinAcceptor],
                            mock_obj: DynamicMixinAcceptor,
                            args: Tuple[object, ...],
                            kwargs: Dict[str, object],
                            mixin_init_kwarg_params: Dict[str, Parameter] = {}):

    non_self_param_keys = \
        (['args'] if args else []) + list(mixin_init_kwarg_params.keys()) + ['kwargs']
    assert tuple(signature(MockCls.__init__).parameters.keys()) == \
           tuple(['self'] + non_self_param_keys)
    assert tuple(signature(mock_obj.__init__).parameters.keys()) == \
           tuple(non_self_param_keys)

    assert mock_obj._mixin_init_kwarg_params == mixin_init_kwarg_params
    assert mock_obj.args == args
    assert mock_obj.kwargs == kwargs


def test_new_method_no_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


def test_multiple_new_method_no_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)
    MockPlainCls.accept_mixin(MockOtherNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(MockPlainCls, mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True))

    assert mock_plain_obj.new_method() == 'other new method'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


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


def test_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateMixin)

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


def test_access_orig_cls_member_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgAccessOrigClsMemberStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg='something')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg='something'),
        mixin_init_kwarg_params=dict(my_kwarg=Parameter('my_kwarg', Parameter.KEYWORD_ONLY)))

    assert mock_plain_obj.new_method() == 'my_kwarg: something'
    assert mock_plain_obj.to_override() == 'MockPlainClsWithMixins'


def test_fail_missing_kwargs_multiple_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateMixin)
    MockPlainCls.accept_mixin(MockOtherKwArgStateMixin)

    with pytest.raises(TypeError):
        MockPlainCls('a', 1, verbose=True)

    with pytest.raises(TypeError):
        MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    with pytest.raises(TypeError):
        MockPlainCls('a', 1, verbose=True, my_other_kwarg_1='other value')


def test_progressive_multiple_state_mixins_same_default(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockKwArgStateMixin)

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

    MockPlainCls.accept_mixin(MockOtherKwArgStateMixin)

    mock_plain_obj = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(
            verbose=True,
            my_kwarg_1='value',
            my_kwarg_2='default value',
            my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)))

    assert mock_plain_obj.new_method() == 'other value'
    assert mock_plain_obj.to_override() == 'default value'

    mock_plain_obj = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2')

    _assert_args_and_kwargs(
        MockPlainCls,
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)))

    assert mock_plain_obj.new_method() == 'alt1B'
    assert mock_plain_obj.to_override() == 'alt2'


def test_fail_progressive_multiple_state_mixins_diff_defaults(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockKwArgStateMixin)
    MockPlainCls.accept_mixin(MockOtherKwArgDiffDefaultStateMixin)

    with pytest.raises(AttributeError):
        MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')


def test_diff_orig_class_multiple_state_mixins_diff_default(mock_plain_cls, mock_other_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateMixin)

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
    MockOtherPlainCls.accept_mixin(MockOtherKwArgDiffDefaultStateMixin)

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


def test_fail_no_init_method_state_mixin():
    with pytest.raises(TypeError):

        class MockNoInitCls(DynamicMixinAcceptor):
            def to_override(self):
                return self.__class__.__name__


def test_fail_missing_kwargs_init_param_state_mixin():
    class MockNoKwargsInitCls(DynamicMixinAcceptor):
        def __init__(self, *args):
            self.args = args
            self.kwargs = {}

        def to_override(self):
            return self.__class__.__name__

    with pytest.raises(AttributeError):
        MockNoKwargsInitCls.accept_mixin(MockKwArgStateMixin)


def test_fail_pos_only_arg_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    with pytest.raises(AttributeError):
        MockPlainCls.accept_mixin(MockPosOnlyArgStateMixin)


def test_missing_pos_args_init_param_state_mixin():
    class MockNoPosArgsInitCls(DynamicMixinAcceptor):
        def __init__(self, **kwargs):
            self.args = ()
            self.kwargs = kwargs

        def to_override(self):
            return self.__class__.__name__

    MockNoPosArgsInitCls.accept_mixin(MockKwArgStateMixin)

    mock_no_pos_args_init_obj = MockNoPosArgsInitCls(verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        MockNoPosArgsInitCls,
        mock_no_pos_args_init_obj,
        args=(),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')))

    assert mock_no_pos_args_init_obj.new_method() == 'value'
    assert mock_no_pos_args_init_obj.to_override() == 'default value'


def test_predefined_init_kwargs_progressive_multiple_state_mixins_same_default(
        mock_predefined_init_kwargs_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa

    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)

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

    MockPredefinedInitKwargsCls.accept_mixin(MockOtherKwArgStateMixin)

    mock_predefined_init_kwargs_plain_obj = MockPredefinedInitKwargsCls(
        'a', 1, verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        MockPredefinedInitKwargsCls,
        mock_predefined_init_kwargs_plain_obj,
        args=('a', 1),
        kwargs=dict(
            verbose=True,
            my_kwarg_1='value',
            my_kwarg_2='default value',
            my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)))

    assert mock_predefined_init_kwargs_plain_obj.new_method() == 'other value'
    assert mock_predefined_init_kwargs_plain_obj.to_override() == 'default value'


def test_fail_predefined_init_kwargs_state_mixin_diff_default(mock_predefined_init_kwargs_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa

    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)
    MockPredefinedInitKwargsCls.accept_mixin(MockOtherKwArgDiffDefaultStateMixin)

    with pytest.raises(AttributeError):
        MockPredefinedInitKwargsCls('a', 1, verbose=True, my_kwarg_1='value')


def test_other_metaclass_for_base_cls_state_mixin():
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

    MockOtherMetaclassForBaseCls.accept_mixin(MockKwArgStateMixin)

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
