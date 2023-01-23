from omnipy.util.mixin import DynamicMixinAcceptor

#
# Traditional inheritance
#


class A:
    def __init__(self, *, default='A'):
        super().__init__()
        self.default = default

    def obj_method(self):
        return 'A'

    @classmethod
    def cls_method(cls):
        return 'A'

    @staticmethod
    def static_top_level():
        return 'At the top'


class B(A):
    def __init__(self, *, default='B'):
        super().__init__(default=default)
        self.default = default

    def obj_method(self):
        print(f'super().obj_method() == {super().obj_method()}')
        return 'B'

    @classmethod
    def cls_method(cls):
        return 'B'


class C(A):
    def __init__(self, *, default='C'):
        super().__init__(default=default)
        self.default = default

    def obj_method(self):
        print(f'super().obj_method() == {super().obj_method()}')
        return 'C'

    @classmethod
    def cls_method(cls):
        return 'C'


class D(B, C):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs

    def obj_method(self):
        print(f'super().obj_method() == {super().obj_method()}')
        return 'D'


#
# Dynamic mixins
#


class AA:
    def __init__(self, *, default='AA'):
        self.default = default

    def obj_method(self):
        return 'AA'

    @classmethod
    def cls_method(cls):
        return 'AA'

    @staticmethod
    def static_top_level():
        return 'At the top'


class BB(DynamicMixinAcceptor):
    def __init__(self, *, default='BB'):
        self.default = default

    def obj_method(self):
        print(f'super().obj_method() == {super().obj_method()}')
        return 'BB'

    @classmethod
    def cls_method(cls):
        return 'BB'


class CC(DynamicMixinAcceptor):
    def __init__(self, *, default='CC'):
        self.default = default

    def obj_method(self):
        print(f'super().obj_method() == {super().obj_method()}')
        return 'CC'

    @classmethod
    def cls_method(cls):
        return 'C'


class DD(DynamicMixinAcceptor):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def obj_method(self):
        print(f'super().obj_method() == {super().obj_method()}')
        return 'DD'


DD.accept_mixin(BB)
BB.accept_mixin(AA)
DD.accept_mixin(CC)
CC.accept_mixin(AA)

#
# Instantiate and print results
#


def instantiate_and_print_results(d_cls, d_obj_name, header):
    print(header)
    print()

    d_obj = d_cls()

    d_base_classes = d_obj.__class__.__bases__
    print(f'{d_obj_name}.__class__.__bases__={d_base_classes}')

    for i in range(len(d_base_classes)):
        print(
            f'{d_obj_name}.__class__.__bases__[{i}].__bases__={d_obj.__class__.__bases__[i].__bases__}'
        )

    print()
    print(f"{d_obj_name} = {d_cls.__name__}()")
    print(f"{d_obj_name}.obj_method() == '{d_obj.obj_method()}'")
    print(f"{d_obj_name}.cls_method() == '{d_obj.cls_method()}'")
    print(f"{d_obj_name}.static_top_level() == '{d_obj.static_top_level()}'")
    print(f"{d_obj_name}.kwargs == {d_obj.kwargs}")
    print(f"{d_obj_name}.default == '{d_obj.default}'")

    d_obj = d_cls(default='Something else')

    print()
    print(f"{d_obj_name} = {d_cls.__name__}(default='Something else')")
    print(f"{d_obj_name}.default == '{d_obj.default}'")
    print(f"{d_obj_name}.kwargs == {d_obj.kwargs}")
    print()


instantiate_and_print_results(D, 'd', 'Traditional inheritance:')
instantiate_and_print_results(DD, 'dd', 'Dynamic mixins:')
