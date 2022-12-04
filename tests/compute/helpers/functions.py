import inspect


def assert_updated_wrapper(a, b):
    assert a.__name__ == b.__name__
    assert a.__qualname__ == b.__qualname__
    assert a.__module__ == b.__module__
    assert a.__doc__ == b.__doc__
    assert a.__annotations__ == b.__annotations__

    equal_signatures = inspect.signature(a) == inspect.signature(b)
    assert equal_signatures
