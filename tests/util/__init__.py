from typing import Generic, TypeVar

from omnipy.util.param_key_mapper import ParamKeyMapper

# For test_mako_helpers.test_internally_inherited

T = TypeVar('T')


class GrandParent:
    inherited_grandparent_class_variable: bool = True

    @property
    def inherited_grandparent_property(self) -> bool:
        return True

    @classmethod
    def inherited_grandparent_classmethod(cls) -> bool:
        return True

    @staticmethod
    def inherited_grandparent_staticmethod() -> bool:
        return True

    def inherited_grandparent_method(self) -> bool:
        return self.inherited_grandparent_instance_variable


class ParentGeneric(GrandParent, Generic[T]):
    inherited_parent_class_variable: T

    @property
    def inherited_parent_generic_property(self) -> bool:
        return True

    @classmethod
    def inherited_parent_generic_classmethod(cls, input_obj: T) -> T:
        return input_obj

    @staticmethod
    def inherited_parent_generic_staticmethod(input_obj: T) -> T:
        return input_obj

    def inherited_parent_generic_method(self) -> bool:
        return True


class Parent(ParamKeyMapper):
    inherited_parent_class_variable: bool = True

    @property
    def inherited_parent_property(self) -> bool:
        return True

    @classmethod
    def inherited_parent_classmethod(cls) -> bool:
        return True

    @staticmethod
    def inherited_parent_staticmethod() -> bool:
        return True

    def inherited_parent_method(self) -> bool:
        return True
