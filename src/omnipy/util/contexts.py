from contextlib import AbstractContextManager, contextmanager
from copy import deepcopy

from omnipy.util.helpers import all_equals

# TODO: Consider refactoring as many as possible of the context managers (AbstractContextManager
#       subclasses) to @contextmanager-decorated methods


class LastErrorHolder(AbstractContextManager):
    def __init__(self):
        self._last_error = None

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self._last_error = exc_val
        return True

    def raise_derived(self, exc: Exception):
        if self._last_error is not None:
            raise exc from self._last_error
        else:
            raise exc


Undefined = object()


# TODO: Perhaps the two use cases of this are so dissimilar that the class should be split into two
#       distinct subclasses to make the code easier to understand?
class AttribHolder(AbstractContextManager):
    def __init__(self,
                 obj: object,
                 attr_name: str,
                 other_value: object = Undefined,
                 reset_to_other: bool = False,
                 switch_to_other: bool = False,
                 on_class: bool = False,
                 copy_attr: bool = False):
        self._obj_or_cls = obj.__class__ if on_class else obj
        self._attr_name = attr_name
        self._other_value = None if other_value is Undefined else other_value
        self._prev_value: object | None = None
        self._reset_to_other = reset_to_other
        self._switch_to_other = switch_to_other
        self._copy_attr = copy_attr
        self._store_prev_attr = False
        self._set_attr_to_other = False

        assert not (reset_to_other and switch_to_other), \
            'Only one of `reset_to_other` and `switch_to_other` can be specified.'

        if other_value is not Undefined:
            assert reset_to_other or switch_to_other, \
                ('If other_value is specified, you also need to set one of `reset_to_other` and '
                 '`switch_to_other`')

        if reset_to_other or switch_to_other:
            assert other_value is not Undefined, \
                ('If one of `reset_to_other` and `switch_to_other` are specified, you also need '
                 'to provide a value for `other_value`')

    def __enter__(self):
        if hasattr(self._obj_or_cls, self._attr_name):
            attr_value = getattr(self._obj_or_cls, self._attr_name)

            self._store_prev_attr = \
                not self._reset_to_other and not all_equals(attr_value, self._other_value)

            if self._store_prev_attr:
                self._prev_value = deepcopy(attr_value) if self._copy_attr else attr_value

            if self._switch_to_other:
                setattr(self._obj_or_cls, self._attr_name, self._other_value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._switch_to_other or exc_val is not None:
            reset_value = self._other_value if self._reset_to_other else self._prev_value
            setattr(self._obj_or_cls, self._attr_name, reset_value)

        if self._store_prev_attr:
            self._prev_value = None


@contextmanager
def nothing(*args, **kwds):
    yield None


class PrintExceptionContext(AbstractContextManager):
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{exc_type.__name__}: {str(exc_val).splitlines()[0]}', end='')
        return True


print_exception = PrintExceptionContext()
