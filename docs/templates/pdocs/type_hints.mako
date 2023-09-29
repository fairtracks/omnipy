##
## get_type_name_from_annotation
##

<%!
def get_type_name_from_annotation(annotation, empty_obj):
    if annotation is not empty_obj:
        # (f'Before: {repr(annotation)}')
        type_name = convert_to_qual_name_type_hint_str(annotation)
        # print(f'After: {repr(type_name)}')
    else:
        type_name = ''

    return type_name
%>


##
## convert_to_qual_name_type_hint_str
##

<%!
from inspect import formatannotation
from typing import get_type_hints, Any


def convert_to_qual_name_type_hint_str(type_hint: Any) -> str:
    def fixed_get_type_hints (obj: Any) -> str:
        """
        Workaround from https://stackoverflow.com/a/66845686, due to limitations in get_type_hints()
        per Python 3.10
        """
        try:
            class X:
                x: obj
            return get_type_hints ( X )['x']
        except NameError as e:
            print(e)
            return obj

    return formatannotation(fixed_get_type_hints(type_hint))
%>


##
## cleanup_type_hint_str_before_parsing
##

<%!

_TYPE_HINTS_REPLACE_MAP = {
    '~': '',
    '+': '',
    '-': '',
}

def cleanup_type_hint_str_before_parsing(type_hint):
    for from_str, to_str in _TYPE_HINTS_REPLACE_MAP.items():
        type_hint = type_hint.replace(from_str, to_str)
    return type_hint
%>


##
## parse_type_hint
##

<%!
import ast

def parse_type_hint(type_hint_string):
    """
    Parses a Python type hint string and returns the individual types as a list of strings.

    Generated by ChatGPT May 21, 2023, in a guided session. This is the 22nd attempt.

    Args:
        type_hint_string (str): The type hint string to parse.

    Returns:
        list: The individual types parsed from the type hint string.

    Example:
        type_hint = "Union[typing.List[str], typing.Dict[str, int], Tuple[int, str], Optional[int]]"
        parsed_types = parse_type_hint(type_hint)
        print(parsed_types)
        # Output: ['Union', 'typing.List', 'str', 'typing.Dict', 'str', 'int', 'Tuple', 'int', 'str', 'Optional', 'int']
    """
    # print(f'Parsing: {repr(type_hint_string)}')
    source = f"def f() -> {type_hint_string}: pass"
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
            type_strings.append(".".join(reversed(qual_names + [node.id])))

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
%>


##
## module_url()
##

<%!
def module_url(parent, m):
    """
    Adapted from https://github.com/timothycrosley/pdocs/blob/master/pdocs/html_helpers.py
    """

    import os
    import pdocs

    relpath = os.path.relpath(m.name.replace(".", "/"), parent.name.replace(".", "/"))
    if relpath == ".":
        return ""
    else:
        return relpath + "/"
%>


##
## lookup()
##

<%!
def lookup(module, refname):
    """
    Adapted from https://github.com/timothycrosley/pdocs/blob/master/pdocs/html_helpers.py
    """

    import pdocs

    if not '.' in refname:
        refname = f'{module.name}.{refname}'

    d = module.find_ident(refname)

    if isinstance(d, pdocs.doc.External):
        return None, None
    if isinstance(d, pdocs.doc.Module):
        return d.refname, module_url(module, d)

    return d.name, f"{module_url(module, d.module)}#{d.name.lower()}"
%>