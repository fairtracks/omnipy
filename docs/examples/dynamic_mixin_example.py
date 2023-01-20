from omnipy.util.mixin import DynamicMixinAcceptor


class A:
    def __init__(self, *, k='A'):
        super().__init__()
        self.k = k

    def obj_method(self):
        return 'A'

    @classmethod
    def cls_method(cls):
        return 'A'

    @staticmethod
    def static_top_level():
        return 'At the top'


class B(A):
    def __init__(self, *, k='B'):
        super().__init__(k=k)
        self.k = k

    def obj_method(self):
        return 'B'

    @classmethod
    def cls_method(cls):
        return 'B'


class C(A):
    def __init__(self, *, k='C'):
        super().__init__(k=k)
        self.k = k

    def obj_method(self):
        return 'C'

    @classmethod
    def cls_method(cls):
        return 'C'


class D(B, C):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs

    def obj_method(self):
        return 'D'


class AA:
    def __init__(self, *, k='AA'):
        self.k = k

    def obj_method(self):
        return 'AA'

    @classmethod
    def cls_method(cls):
        return 'AA'

    @staticmethod
    def static_top_level():
        return 'At the top'


class BB(DynamicMixinAcceptor):
    def __init__(self, *, k='BB'):
        self.k = k

    def obj_method(self):
        return 'BB'

    @classmethod
    def cls_method(cls):
        return 'BB'


class CC(DynamicMixinAcceptor):
    def __init__(self, *, k='CC'):
        self.k = k

    def obj_method(self):
        return 'CC'

    @classmethod
    def cls_method(cls):
        return 'C'


class DD(DynamicMixinAcceptor):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def obj_method(self):
        return 'DD'


BB.accept_mixin(AA)
CC.accept_mixin(AA)
DD.accept_mixin(BB)
DD.accept_mixin(CC)


def instantiate_and_print_results(d_cls, header):
    print(header)
    print()

    d = d_cls()

    d_base_classes = d.__class__.__bases__
    print(f'd.__class__.__bases__={d_base_classes}')

    for i in range(len(d_base_classes)):
        print(f'd.__class__.__bases__[{i}].__bases__={d.__class__.__bases__[i].__bases__}')

    print()
    print(f'd.obj_method()={d.obj_method()}')
    print(f'd.cls_method()={d.cls_method()}')
    print(f'd.static_top_level()={d.static_top_level()}')
    print(f'd.kwargs={d.kwargs}')
    print(f'd.k={d.k}')
    print()


instantiate_and_print_results(D, 'Traditional inheritance:')
instantiate_and_print_results(DD, 'Dynamic mixins:')
