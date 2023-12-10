from copy import copy


class LastErrorHolder:
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


class AttribHolder:
    def __init__(self,
                 obj: object,
                 attr_name: str,
                 other_attr: object = None,
                 on_class: bool = False,
                 copy_attr: bool = False):
        self._obj_or_cls = obj.__class__ if on_class else obj
        self._attr_name = attr_name
        self._other_attr = other_attr
        self._prev_attr: object | None = None
        self._copy_attr = copy_attr
        self._store_prev_attr = False
        self._set_attr_to_other = False

    def __enter__(self):
        if hasattr(self._obj_or_cls, self._attr_name):
            attr = getattr(self._obj_or_cls, self._attr_name)

            self._set_attr_to_other = self._other_attr is not None and self._other_attr != attr
            self._store_prev_attr = self._other_attr is None or self._set_attr_to_other

            if self._store_prev_attr:
                self._prev_attr = copy(attr) if self._copy_attr else attr

            if self._set_attr_to_other:
                setattr(self._obj_or_cls, self._attr_name, self._other_attr)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._set_attr_to_other or exc_val is not None:
            setattr(self._obj_or_cls, self._attr_name, self._prev_attr)

        if self._store_prev_attr:
            self._prev_attr = None


class PrintExceptionContext:
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{exc_type.__name__}: {str(exc_val).splitlines()[0]}', end='')
        return True


print_exception = PrintExceptionContext()
