from abc import ABCMeta
from inspect import Parameter, signature
from typing import Dict, Generic, get_args, Optional, Tuple, Type, TypeVar

import pytest

from omnipy.util.mixin import DynamicMixinAcceptor


@pytest.fixture(scope='function')
def mock_plain_cls() -> Type:
    class MockPlainCls(DynamicMixinAcceptor):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    return MockPlainCls


@pytest.fixture(scope='function')
def mock_other_plain_cls() -> Type:
    class MockOtherPlainCls(DynamicMixinAcceptor):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    return MockOtherPlainCls


@pytest.fixture(scope='function')
def mock_predefined_init_kwargs_cls() -> Type:
    class MockPredefinedInitKwargsCls(DynamicMixinAcceptor):
        args = ()

        def __init__(self, *, my_kwarg_1, my_kwarg_2='default value', **kwargs):
            kwargs |= {'my_kwarg_1': my_kwarg_1, 'my_kwarg_2': my_kwarg_2}
            if hasattr(self, 'kwargs'):
                self.plain_kwargs = self.kwargs
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    return MockPredefinedInitKwargsCls


T = TypeVar('T')


@pytest.fixture(scope='function')
def mock_predefined_init_kwargs_generic_cls() -> Type:
    class MockPredefinedInitKwargsGenericCls(DynamicMixinAcceptor, Generic[T]):
        args = ()

        def __init__(self, *, my_kwarg_1, my_kwarg_2='default value', **kwargs):
            kwargs |= {'my_kwarg_1': my_kwarg_1, 'my_kwarg_2': my_kwarg_2}
            if hasattr(self, 'kwargs'):
                self.plain_kwargs = self.kwargs
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    return MockPredefinedInitKwargsGenericCls


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
    def override(self):
        return 'overridden method'


class MockKwArgStateMixin:
    def __init__(self, *, my_kwarg_1, my_kwarg_2='default value'):
        self._my_kwarg_1 = my_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return f'({self._my_kwarg_1}, {self._my_kwarg_2})'

    def override(self):
        return 'overridden method'


class MockOtherKwArgStateMixin:
    def __init__(self, *, my_other_kwarg_1, my_kwarg_2='default value'):
        self._my_other_kwarg_1 = my_other_kwarg_1
        self._my_kwarg_2 = my_kwarg_2

    def new_method(self):
        return f'({self._my_other_kwarg_1}, {self._my_kwarg_2})'

    def override(self):
        return 'overridden method'


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
        return f'({self._my_other_kwarg_1}, {self._my_kwarg_2})'

    def override(self):
        return 'overridden method'


class MockPosOnlyArgStateMixin:
    def __init__(self, my_pos_only_arg, /):
        self._my_pos_only_arg = my_pos_only_arg


def test_cls_with_mixins_name_and_module(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)
    assert mock_plain_obj.__class__.__name__ == 'MockPlainClsWithMixins'
    assert mock_plain_obj.__class__.__module__ == 'tests.util.test_dynamic_mixin'


def test_no_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert not hasattr(mock_plain_obj, 'new_method')
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'


def _assert_args_and_kwargs(mock_obj: object,
                            args: Tuple[object, ...],
                            kwargs: Dict[str, object],
                            mock_cls: Optional[Type] = None,
                            mixin_init_kwarg_params: Dict[str, Parameter] = {},
                            mixin_init_kwarg_params_including_bases: Dict[str, Parameter] = {},
                            args_in_signature=True):

    if mixin_init_kwarg_params and not mixin_init_kwarg_params_including_bases:
        mixin_init_kwarg_params_including_bases = mixin_init_kwarg_params

    non_self_param_keys = (['args'] if args_in_signature else []) + list(
        mixin_init_kwarg_params_including_bases.keys()) + ['kwargs']

    assert mock_obj._mixin_init_kwarg_params == mixin_init_kwarg_params
    assert mock_obj._mixin_init_kwarg_params_including_bases == \
           mixin_init_kwarg_params_including_bases
    assert mock_obj.args == args
    assert mock_obj.kwargs == kwargs

    assert tuple(signature(mock_obj.__init__).parameters.keys()) == \
           tuple(non_self_param_keys)

    if mock_cls:
        assert tuple(signature(mock_cls.__init__).parameters.keys()) == \
           tuple(['self'] + non_self_param_keys)


def test_new_method_no_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'


def test_multiple_new_method_no_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockOtherNewMethodNoStateMixin)
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == 'other new method'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'


def test_override_no_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert not hasattr(mock_plain_obj, 'new_method')
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'


def test_progressive_multiple_new_method_and_override_no_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'

    MockPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_plain_obj_2 = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj_2, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert mock_plain_obj_2.new_method() == 'new method'
    assert mock_plain_obj_2.override() == 'overridden by: MockPlainClsWithMixins'


def test_reset_multiple_no_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)
    MockPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'

    MockPlainCls.reset_mixins()

    mock_plain_obj_2 = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj_2, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert not hasattr(mock_plain_obj_2, 'new_method')
    assert mock_plain_obj_2.override() == 'overridden by: MockPlainClsWithMixins'


def test_multiple_orig_class_different_no_state_mixins(mock_plain_cls, mock_other_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockNewMethodNoStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == 'new method'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'

    MockOtherPlainCls = mock_other_plain_cls  # noqa
    MockOtherPlainCls.accept_mixin(MockOverrideNoStateMixin)

    mock_other_plain_obj = MockOtherPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_other_plain_obj, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockOtherPlainCls)

    assert not hasattr(mock_other_plain_obj, 'new_method')
    assert mock_other_plain_obj.override() == 'overridden by: MockOtherPlainClsWithMixins'


def test_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == '(value, default value)'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'


def test_access_orig_cls_member_state_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgAccessOrigClsMemberStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg='something')

    _assert_args_and_kwargs(
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg='something'),
        mixin_init_kwarg_params=dict(my_kwarg=Parameter('my_kwarg', Parameter.KEYWORD_ONLY)),
        mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == 'my_kwarg: something'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'


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
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == '(value, default value)'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'

    MockPlainCls.accept_mixin(MockOtherKwArgStateMixin)

    mock_plain_obj_2 = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        mock_plain_obj_2,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)),
        mock_cls=MockPlainCls)

    assert mock_plain_obj_2.new_method() == '(value, default value)'
    assert mock_plain_obj_2.override() == 'overridden by: MockPlainClsWithMixins'

    mock_plain_obj_3 = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2')

    _assert_args_and_kwargs(
        mock_plain_obj_3,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)),
        mock_cls=MockPlainCls)

    assert mock_plain_obj_3.new_method() == '(alt1A, alt2)'
    assert mock_plain_obj_3.override() == 'overridden by: MockPlainClsWithMixins'


def test_reset_multiple_state_mixins(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    MockPlainCls.accept_mixin(MockKwArgStateMixin)
    MockPlainCls.accept_mixin(MockOtherKwArgStateMixin)

    mock_plain_obj = MockPlainCls(
        'a', 1, verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2')

    _assert_args_and_kwargs(
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='alt1A', my_other_kwarg_1='alt1B', my_kwarg_2='alt2'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)),
        mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == '(alt1A, alt2)'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'

    MockPlainCls.reset_mixins()

    mock_plain_obj_2 = MockPlainCls('a', 1, verbose=True)

    _assert_args_and_kwargs(
        mock_plain_obj_2, args=('a', 1), kwargs=dict(verbose=True), mock_cls=MockPlainCls)

    assert not hasattr(mock_plain_obj_2, 'new_method')
    assert mock_plain_obj_2.override() == 'overridden by: MockPlainClsWithMixins'


def test_diff_orig_class_multiple_state_mixins_diff_default(mock_plain_cls, mock_other_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa
    MockPlainCls.accept_mixin(MockKwArgStateMixin)

    mock_plain_obj = MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_kwarg_1='value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockPlainCls)

    assert mock_plain_obj.new_method() == '(value, default value)'
    assert mock_plain_obj.override() == 'overridden by: MockPlainClsWithMixins'

    MockOtherPlainCls = mock_other_plain_cls  # noqa
    MockOtherPlainCls.accept_mixin(MockOtherKwArgDiffDefaultStateMixin)

    mock_other_plain_obj = MockOtherPlainCls('a', 1, verbose=True, my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        mock_other_plain_obj,
        args=('a', 1),
        kwargs=dict(verbose=True, my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter(
                'my_kwarg_2', Parameter.KEYWORD_ONLY, default='other default value')),
        mock_cls=MockOtherPlainCls)

    assert mock_other_plain_obj.new_method() == '(other value, other default value)'
    assert mock_other_plain_obj.override() == 'overridden by: MockOtherPlainClsWithMixins'


def test_fail_no_init_method_state_mixin():
    with pytest.raises(TypeError):

        class MockNoInitCls(DynamicMixinAcceptor):
            def to_override(self):
                return self.__class__.__name__


def test_fail_pos_only_arg_mixin(mock_plain_cls):
    MockPlainCls = mock_plain_cls  # noqa

    with pytest.raises(AttributeError):
        MockPlainCls.accept_mixin(MockPosOnlyArgStateMixin)


def test_missing_pos_args_init_param_state_mixin():
    class MockNoPosArgsInitCls(DynamicMixinAcceptor):
        def __init__(self, **kwargs):
            self.args = ()
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    MockNoPosArgsInitCls.accept_mixin(MockKwArgStateMixin)

    mock_no_pos_args_init_obj = MockNoPosArgsInitCls(verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_no_pos_args_init_obj,
        args=(),
        kwargs=dict(verbose=True, my_kwarg_1='value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockNoPosArgsInitCls,
        args_in_signature=False)

    assert mock_no_pos_args_init_obj.new_method() == '(value, default value)'
    assert mock_no_pos_args_init_obj.override() == 'overridden by: MockNoPosArgsInitClsWithMixins'


def test_predefined_init_kwargs_progressive_multiple_state_mixins_same_default(
        mock_predefined_init_kwargs_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa

    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)

    mock_predefined_init_kwargs_plain_obj = MockPredefinedInitKwargsCls(
        verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_predefined_init_kwargs_plain_obj,
        args=(),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockPredefinedInitKwargsCls,
        args_in_signature=False)

    assert mock_predefined_init_kwargs_plain_obj.new_method() == '(value, default value)'
    assert mock_predefined_init_kwargs_plain_obj.override() == \
           'overridden by: MockPredefinedInitKwargsClsWithMixins'

    MockPredefinedInitKwargsCls.accept_mixin(MockOtherKwArgStateMixin)

    mock_predefined_init_kwargs_plain_obj = MockPredefinedInitKwargsCls(
        verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    _assert_args_and_kwargs(
        mock_predefined_init_kwargs_plain_obj,
        args=(),
        kwargs=dict(
            verbose=True,
            my_kwarg_1='value',
            my_kwarg_2='default value',
            my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)),
        mock_cls=MockPredefinedInitKwargsCls,
        args_in_signature=False)

    assert mock_predefined_init_kwargs_plain_obj.new_method() == '(value, default value)'
    assert mock_predefined_init_kwargs_plain_obj.override() == \
           'overridden by: MockPredefinedInitKwargsClsWithMixins'


def test_predefined_init_kwargs_progressive_multiple_state_mixins_different_withmixin_classes(
        mock_predefined_init_kwargs_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa

    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)

    mock_obj_1 = MockPredefinedInitKwargsCls(verbose=True, my_kwarg_1='value')

    MockPredefinedInitKwargsCls.accept_mixin(MockOtherKwArgStateMixin)

    mock_obj_2 = MockPredefinedInitKwargsCls(
        verbose=True, my_kwarg_1='value', my_other_kwarg_1='other value')

    assert mock_obj_1.__class__.__name__ == mock_obj_2.__class__.__name__
    assert mock_obj_1.__class__ != mock_obj_2.__class__

    _assert_args_and_kwargs(
        mock_obj_1,
        args=(),
        kwargs=dict(verbose=True, my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=mock_obj_1.__class__,
        args_in_signature=False)

    _assert_args_and_kwargs(
        mock_obj_2,
        args=(),
        kwargs=dict(
            verbose=True,
            my_kwarg_1='value',
            my_kwarg_2='default value',
            my_other_kwarg_1='other value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value'),
            my_other_kwarg_1=Parameter('my_other_kwarg_1', Parameter.KEYWORD_ONLY)),
        mock_cls=mock_obj_2.__class__,
        args_in_signature=False)


def test_nested_mixins(mock_predefined_init_kwargs_cls, mock_plain_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa
    MockPlainCls = mock_plain_cls  # noqa

    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)
    MockPlainCls.accept_mixin(MockPredefinedInitKwargsCls)

    mock_obj = MockPlainCls('a', 1, verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_obj,
        args=('a', 1),
        kwargs=dict(my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockPlainCls)

    assert mock_obj.plain_kwargs == dict(verbose=True, my_kwarg_1='value')
    assert mock_obj.new_method() == '(value, default value)'
    assert mock_obj.override() == 'overridden by: MockPlainClsWithMixins'


def test_nested_mixins_static_outer_inheritance(mock_predefined_init_kwargs_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa
    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)

    class MockMockPlainCls(MockPredefinedInitKwargsCls):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    mock_obj = MockMockPlainCls(verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_obj,
        args=(),
        kwargs=dict(my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(),
        mixin_init_kwarg_params_including_bases=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockMockPlainCls)

    assert mock_obj.plain_kwargs == dict(verbose=True, my_kwarg_1='value')
    assert mock_obj.new_method() == '(value, default value)'
    assert mock_obj.override() == 'overridden by: MockMockPlainClsWithMixins'


def test_nested_mixins_double_static_outer_inheritance(mock_predefined_init_kwargs_cls):
    MockPredefinedInitKwargsCls = mock_predefined_init_kwargs_cls  #noqa
    MockPredefinedInitKwargsCls.accept_mixin(MockKwArgStateMixin)

    class MockMockPlainCls(MockPredefinedInitKwargsCls):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    class MockMockMockPlainCls(MockMockPlainCls):
        ...

    mock_obj = MockMockMockPlainCls(verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_obj,
        args=(),
        kwargs=dict(my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(),
        mixin_init_kwarg_params_including_bases=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockMockPlainCls)

    assert mock_obj.plain_kwargs == dict(my_kwarg_1='value')
    assert mock_obj.new_method() == '(value, default value)'
    assert mock_obj.override() == 'overridden by: MockMockMockPlainClsWithMixins'


def test_nested_mixins_static_outer_inheritance_from_generic(
        mock_predefined_init_kwargs_generic_cls):
    MockPredefinedInitKwargsGenericCls = mock_predefined_init_kwargs_generic_cls  #noqa
    MockPredefinedInitKwargsGenericCls.accept_mixin(MockKwArgStateMixin)

    class MockMockPlainCls(MockPredefinedInitKwargsGenericCls[int]):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def override(self):
            return f'overridden by: {self.__class__.__name__}'

    mock_obj = MockMockPlainCls(verbose=True, my_kwarg_1='value')

    _assert_args_and_kwargs(
        mock_obj,
        args=(),
        kwargs=dict(my_kwarg_1='value', my_kwarg_2='default value'),
        mixin_init_kwarg_params=dict(),
        mixin_init_kwarg_params_including_bases=dict(
            my_kwarg_1=Parameter('my_kwarg_1', Parameter.KEYWORD_ONLY),
            my_kwarg_2=Parameter('my_kwarg_2', Parameter.KEYWORD_ONLY, default='default value')),
        mock_cls=MockMockPlainCls)

    assert mock_obj.plain_kwargs == dict(verbose=True, my_kwarg_1='value')
    assert mock_obj.new_method() == '(value, default value)'
    assert mock_obj.override() == 'overridden by: MockMockPlainClsWithMixins'
    assert get_args(mock_obj.__class__.__orig_bases__[1]) == (int,)
