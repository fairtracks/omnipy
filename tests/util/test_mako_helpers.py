# from collections import UserDict
# from dataclasses import dataclass
# from typing import Type
#
# import pytest
# import pytest_cases as pc
#
# from omnipy.util.mako_helpers import is_internally_inherited
# from tests.util import Parent, ParentGeneric
#
# # For test_internally_inherited
#
#
# class Child(Parent, ParentGeneric[int], UserDict):
#     not_inherited_class_variable: bool = True
#
#     @property
#     def not_inherited_property(self) -> bool:
#         return True
#
#     @classmethod
#     def not_inherited_classmethod(cls) -> bool:
#         return True
#
#     @staticmethod
#     def not_inherited_staticmethod() -> bool:
#         return True
#
#     def not_inherited_method(self) -> bool:
#         return self.not_inherited_instance_variable
#
#
# @dataclass
# class InheritanceCase:
#     element_name: str
#     internal_packages: list[str]
#     internally_inherited: bool | None = None
#     raise_exception: Type[Exception] | None = None
#
#
# @pc.case(id='type_class_variable', tags=['element_type'])
# def case_type_class_variable() -> str:
#     return 'class_variable'
#
#
# @pc.case(id='type_property', tags=['element_type'])
# def case_type_property() -> str:
#     return 'property'
#
#
# @pc.case(id='type_classmethod', tags=['element_type'])
# def case_type_classmethod() -> str:
#     return 'classmethod'
#
#
# @pc.case(id='type_staticmethod', tags=['element_type'])
# def case_type_staticmethod() -> str:
#     return 'staticmethod'
#
#
# @pc.case(id='type_method', tags=['element_type'])
# def case_type_method() -> str:
#     return 'method'
#
#
# @pc.case(id='packages_empty', tags=['packages'])
# def case_packages_empty() -> list[str]:
#     return []
#
#
# @pc.case(id='packages_tests', tags=['packages'])
# def case_packages_tests() -> list[str]:
#     return ['tests']
#
#
# @pc.case(id='packages_tests_omnipy', tags=['packages'])
# def case_packages_tests_omnipy() -> list[str]:
#     return ['tests', 'omnipy']
#
#
# @pc.case(id='packages_collections', tags=['packages'])
# def case_packages_collections() -> list[str]:
#     return ['collections']
#
#
# @pc.parametrize_with_cases('element_type', cases='.', has_tag='element_type')
# @pc.parametrize_with_cases('internal_packages', cases='.', has_tag='packages')
# @pc.case(id='not_inherited', tags=['element'])
# def case_not_inherited(element_type: str, internal_packages: list[str]) -> InheritanceCase:
#     return InheritanceCase(f'not_inherited_{element_type}', internal_packages, False)
#
#
# @pc.parametrize_with_cases('element_type', cases='.', has_tag='element_type')
# @pc.parametrize_with_cases('internal_packages', cases='.', has_tag='packages')
# @pc.case(id='inherited_parent', tags=['element'])
# def case_inherited_parent(element_type: str, internal_packages: list[str]) -> InheritanceCase:
#     return InheritanceCase(f'inherited_parent_{element_type}',
#                            internal_packages,
#                            True if 'tests' in internal_packages else False)
#
#
# @pc.parametrize_with_cases('internal_packages', cases='.', has_tag='packages')
# @pc.case(id='inherited_collections', tags=['element'])
# def case_inherited_collections(internal_packages: list[str]) -> InheritanceCase:
#     return InheritanceCase('update',
#                            internal_packages,
#                            True if 'collections' in internal_packages else False)
#
#
# @pc.parametrize_with_cases('internal_packages', cases='.', has_tag='packages')
# @pc.case(id='inherited_parent_omnipy', tags=['element'])
# def case_inherited_parent_omnipy(internal_packages: list[str]) -> InheritanceCase:
#     return InheritanceCase('map_matching_keys',
#                            internal_packages,
#                            True if 'omnipy' in internal_packages else False)
#
#
# @pc.parametrize_with_cases('element_type', cases='.', has_tag='element_type')
# @pc.parametrize_with_cases('internal_packages', cases='.', has_tag='packages')
# @pc.case(id='no_such_method', tags=['element'])
# def case_no_such_method(element_type: str, internal_packages: list[str]) -> InheritanceCase:
#     return InheritanceCase(f'no_such_{element_type}', internal_packages, None, AttributeError)
#
#
# @pc.parametrize_with_cases('inheritance_case', cases='.', has_tag='element')
# def test_is_internally_inherited(inheritance_case: InheritanceCase):
#     if inheritance_case.internally_inherited is not None:
#         ret = _assert_internally_inherited(inheritance_case)
#         assert ret == inheritance_case.internally_inherited
#     elif inheritance_case.raise_exception:
#         with pytest.raises(inheritance_case.raise_exception):
#             _assert_internally_inherited(inheritance_case),
#
#
# def _assert_internally_inherited(inheritance_case):
#     return is_internally_inherited(Child,
#                                    inheritance_case.element_name,
#                                    inheritance_case.internal_packages)
