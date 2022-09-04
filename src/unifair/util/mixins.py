from typing import Any, Callable, Union


class DynamicClassDecoratorMixin:
    def __new__(
        cls: 'DynamicClassDecoratorMixin', *args: Any, **kwargs: Any
    ) -> Union['DynamicClassDecoratorMixin', Callable[..., 'DynamicClassDecoratorMixin']]:
        args = list(args)

        def new_obj(func: Callable) -> 'DynamicClassDecoratorMixin':
            obj = object.__new__(cls)
            obj.__init__(func, *args, **kwargs)
            return obj

        if len(args) > 0 and callable(args[0]):
            _func = args[0]
            args.pop(0)
            return new_obj(_func)

        return new_obj

    def __call__(self, *args, **kwargs):
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))
