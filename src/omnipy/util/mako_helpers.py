import ast
from inspect import formatannotation, getmodule, isclass, isgeneratorfunction, Signature
import os
from types import ModuleType
from typing import Any, get_type_hints

from docstring_parser import DocstringParam, DocstringReturns
from pdocs.doc import Doc, External, Function, Module

from omnipy.util.helpers import create_merged_dict

IGNORED = None
IGNORE_PARAMS = ['cls', 'self']


def filter_internal_external(cls: type, members: list[Doc]):
    internal_members = []
    external_members = []

    for member in members:
        try:
            if is_member(cls, member.name) or is_internally_inherited(cls, member.name, ['omnipy']):
                internal_members.append(member)
            else:
                external_members.append(member)
        except AttributeError as e:
            print(e)

    return internal_members, external_members


def is_member(cls: type, member_name: str):
    return member_name in vars(cls)


def is_internally_inherited(cls: type,
                            member_name: str,
                            internal_packages: list[str],
                            outer: bool = True):
    if outer and member_name not in dir(cls):
        raise AttributeError(f'"{member_name}" is not a member of class "{cls.__name__}"')

    if is_member(cls, member_name):
        if outer:
            return False
        else:
            is_internal = any(cls.__module__.startswith(pkg) for pkg in internal_packages)
            return is_internal
    else:
        for base_cls in cls.__bases__:
            if is_internally_inherited(base_cls, member_name, internal_packages, outer=False):
                return True
        return False


def merge_signature_with_docstring(func: Function,
                                   signature: Signature,
                                   ds_params: list[DocstringParam],
                                   ds_returns: DocstringReturns):
    ds_params_map = {ds_param.arg_name: ds_param for ds_param in ds_params}
    params = []

    for name, param in signature.parameters.items():
        if name in IGNORE_PARAMS:
            continue

        description = ''
        if name in ds_params_map:
            description = ds_params_map[name].description

        type_name = get_type_name_from_annotation(func.module.module, param.annotation, param.empty)

        default = param.default if param.default is not param.empty else ''

        params.append(
            DocstringParam(
                args=[],
                description=description,
                arg_name=name,
                type_name=type_name,
                is_optional=IGNORED,
                default=default))

    description = ds_returns.description if ds_returns else ''

    if type_name := get_type_name_from_annotation(func.module.module,
                                                  signature.return_annotation,
                                                  signature.empty):
        returns = DocstringReturns(
            args=[],
            description=description,
            type_name=type_name,
            is_generator=isgeneratorfunction(func.func),
            return_name=IGNORED)
    else:
        returns = None

    return params, returns


def get_type_name_from_annotation(module: ModuleType, annotation, empty_obj):
    if annotation is not empty_obj:
        # (f'Before: {repr(annotation)}')
        type_name = convert_to_qual_name_type_hint_str(module, annotation)
        # print(f'After: {repr(type_name)}')
    else:
        type_name = ''

    return type_name


def _is_internal_module(module: ModuleType, imported_modules: list[ModuleType]):
    return module not in imported_modules and module.__name__.startswith('omnipy')


def recursive_module_import(module: ModuleType, imported_modules: list[ModuleType] = []):
    module_vars = vars(module)
    imported_modules.append(module)

    for val in module_vars.values():
        if isclass(val):
            for base_cls in val.__bases__:
                base_cls_module = getmodule(base_cls)
                if base_cls_module and _is_internal_module(base_cls_module, imported_modules):
                    module_vars = create_merged_dict(
                        recursive_module_import(base_cls_module, imported_modules),
                        module_vars,
                    )

    return module_vars


def convert_to_qual_name_type_hint_str(module: ModuleType, type_hint: Any) -> str:
    def fixed_get_type_hints(obj: Any) -> str:
        """
        Workaround from https://stackoverflow.com/a/66845686, due to limitations in get_type_hints()
        per Python 3.10
        """
        try:

            class X:
                x: obj

            return get_type_hints(X, globalns=recursive_module_import(module))['x']
        except NameError as e:
            print(e)
            return obj

    return formatannotation(fixed_get_type_hints(type_hint))


def format_type_as_markdown(module, type_name: str):
    cleaned_type_name = cleanup_type_hint_str_before_parsing(type_name)
    for basic_type_name in set(parse_type_hint(cleaned_type_name)):
        refname, url = lookup(module, basic_type_name)
        if refname:
            type_name = type_name.replace(basic_type_name, f'[{refname}]({url})')
    return type_name


_TYPE_HINTS_REPLACE_MAP = {
    '~': '',
    '+': '',
    '-': '',
}


def cleanup_type_hint_str_before_parsing(type_hint):
    for from_str, to_str in _TYPE_HINTS_REPLACE_MAP.items():
        type_hint = type_hint.replace(from_str, to_str)
    return type_hint


def parse_type_hint(type_hint_string):
    """
    Parses a Python type hint string and returns the individual types as a list of strings.

    Generated by ChatGPT May 21, 2023, in a guided session. This is the 22nd attempt.

    Args:
        type_hint_string (str): The type hint string to parse.

    Returns:
        list: The individual types parsed from the type hint string.

    Example:
        type_hint = "Union[list[str], dict[str, int], tuple[int, str], Optional[int]]"
        parsed_types = parse_type_hint(type_hint)
        print(parsed_types)
        # Output: ['Union', 'list', 'str', 'dict', 'str', 'int', 'tuple', 'int',
                   'str', 'Optional', 'int']
    """
    # print(f'Parsing: {repr(type_hint_string)}')
    source = f'def f() -> {type_hint_string}: pass'
    tree = ast.parse(source)

    type_strings = []

    def process_node(node, qual_names=None):
        """
        Recursively processes the AST nodes and extracts the type names.

        Args:
            node (ast.AST): The AST node to process.
            qual_names (list): A list of qualified names encountered during processing.

        Returns:
            None
        """
        qual_names = qual_names or []

        if isinstance(node, ast.Name):
            type_strings.append('.'.join(reversed(qual_names + [node.id])))

        elif isinstance(node, ast.Subscript):
            process_node(node.value, qual_names)
            process_node(node.slice, qual_names)

        elif isinstance(node, ast.Attribute):
            process_node(node.value, qual_names + [node.attr])

        elif isinstance(node, ast.Tuple):
            for elt in node.elts:
                process_node(elt, qual_names)

    returns_annotation = tree.body[0].returns
    process_node(returns_annotation)

    return type_strings


def lookup(module, refname):
    """
    Adapted from https://github.com/timothycrosley/pdocs/blob/master/pdocs/html_helpers.py
    """

    if '.' not in refname:
        refname = f'{module.name}.{refname}'

    d = module.find_ident(refname)

    if isinstance(d, External):
        return None, None
    if isinstance(d, Module):
        return d.refname, module_url(module, d)

    return d.name, f'{module_url(module, d.module)}#{d.name.lower()}'


def module_url(parent, m):
    """
    Adapted from https://github.com/timothycrosley/pdocs/blob/master/pdocs/html_helpers.py
    """

    relpath = os.path.relpath(m.name.replace('.', '/'), parent.name.replace('.', '/'))
    if relpath == '.':
        return ''
    else:
        return relpath + '/'
