## Adapted from the text.mako template in the "pdocs" repo:
##
##   https://github.com/timothycrosley/pdocs/blob/master/pdocs/templates/text.mako
##
## Copyright for first commit of this file is held by Timothy Crosley, 2019, as detailed below. All
## further modifications is held by Omnipy contributors, as detailed in the main LICENSE file of
## the Omnipy repository (https://github.com/fairtracks/omnipy/blob/main/LICENSE).
##
## MIT License
##
## Copyright (c) 2019 Timothy Crosley
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in all
## copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.

###
### Define mini-templates for each portion of the doco.
###

##
## Disable omnipy root log formatter
##

<%
    from omnipy import runtime
    runtime.config.root_log.log_format_str = None
%>

##
## Constants
##

<%
    IGNORED = None
    MISSING_STR = ''
    IGNORE_PARAMS = ['cls', 'self']
%>

##
## h1(), h2(), h3(), h4()
##

<%def name="h1(s)"># ${s}
</%def>

<%def name="h2(s)">## ${s}
</%def>

<%def name="h3(s)">### ${s}
</%def>

<%def name="h4(s)">#### ${s}
</%def>


##
## par()
##

<%def name="par(s)">
% if s:
${s}

% endif
</%def>


##
## get_type_name_from_annotation
##

<%
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

<%
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

<%

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

<%
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

<%
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

<%
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


##
## table_rows()
##

<%def name="table_rows(elements, show_header=False, kind=None, show_name=False, show_arg_name=False,
                       show_type=False, show_description=False, show_default=False)"> \
% if show_header:
    <%
        col_names = []
        if kind:
            col_names.append('Kind')
        if show_name or show_arg_name:
            col_names.append('Name')
        if show_type:
            col_names.append('Type')
        if show_description:
            col_names.append('Description')
        if show_default:
            col_names.append('Default')
        header = ''.join([f'| {col_name} ' for col_name in col_names] + ['|'])
        divider = ''.join(['|---' for _ in col_names] + ['|'])
    %>
${header}
${divider}
% endif
% if elements:
    % for i, el in enumerate(elements):
        <%
            row = []
            if kind:
                row.append(kind)
            if show_name:
                row.append(f'`{el.name}`')
            if show_arg_name:
                row.append(f'`{el.arg_name}`')
            if show_type:
                if not el.type_name:
                    row.append(MISSING_STR)
                else:
                    type_name = el.type_name
                    cleaned_type_name = cleanup_type_hint_str_before_parsing(type_name)
                    for basic_type_name in set(parse_type_hint(cleaned_type_name)):
                        refname, url = lookup(module, basic_type_name)
                        if refname:
                            type_name = type_name.replace(basic_type_name, f'[{refname}]({url})')
                    row.append(f'<code>{type_name}</code>')
            if show_description:
                if hasattr(el, 'parsed_docstring') and el.parsed_docstring and \
                        el.parsed_docstring.short_description:
                    description = el.parsed_docstring.short_description
                elif hasattr(el, 'description') and el.description:
                    description = el.description
                else:
                    description = MISSING_STR
                row.append(description.replace('\n', '<br>'))
            if show_default:
                row.append(el.default if el.default else MISSING_STR)
            row = ''.join([f'| {val} ' for val in row] + ['|'])
        %> \
${row}
    % endfor
% endif
</%def>


##
## function()
##

<%def name="function(func, class_level=False)" buffered="True">
    <%
        formatted_return = func.return_annotation().strip("'")
        formatted_params = func.params()
        parsed_ds = func.parsed_docstring

        import inspect

        try:
            module_name = func.func.__module__ if hasattr(func.func, '__module__') else func.func.__class__.__module__
            if module_name:
                import importlib
                module = importlib.import_module(module_name)
                globals().update(vars(module))
                # print(f'Importing: {module_name}')

            signature = inspect.signature(func.func)
        except (TypeError, ValueError) as e:
            signature = None
            print(e)

    %>
% if class_level:
${h4(func.name)}
% else:
${h3(func.name)}
% endif


``` python3
def ${func.name}(
    ${",\n    ".join(formatted_params)}
)${' -> ' + formatted_return if formatted_return else ''}
```

% if parsed_ds:
    <%
        from docstring_parser import DocstringParam, DocstringReturns

        short_desc = parsed_ds.short_description
        long_desc = parsed_ds.long_description
        ds_params = parsed_ds.params
        ds_returns = parsed_ds.returns
        raises = parsed_ds.raises

        if signature:
            ds_params_map = {}
            for ds_param in ds_params:
                ds_params_map[ds_param.arg_name] = ds_param

            params = []
            for name, param in signature.parameters.items():
                if name in IGNORE_PARAMS:
                    continue

                description = ''
                if name in ds_params_map:
                    description = ds_params_map[name].description

                type_name = get_type_name_from_annotation(param.annotation, param.empty)

                default = param.default if param.default is not param.empty else ''

                params.append(DocstringParam(args=[],
                                             description=description,
                                             arg_name=name,
                                             type_name=type_name,
                                             is_optional=IGNORED,
                                             default=default))

            description = ds_returns.description if ds_returns else ''

            type_name = get_type_name_from_annotation(signature.return_annotation, signature.empty)

            if type_name:
                returns = DocstringReturns(args=[],
                                           description=description,
                                           type_name=type_name,
                                           is_generator=inspect.isgeneratorfunction(func.func),
                                           return_name=IGNORED)
            else:
                returns = None

        else:
            params = ds_params
            returns = ds_returns
    %>
${par(short_desc)}
${par(long_desc)}
    % if params:
## TODO: Merge params and ret from docstring with func signature, adding missing params, ret and
##       missing members (e.g. type_name, default)

**Parameters:**

${table_rows(params, show_header=True, show_arg_name=True,
             show_type=True, show_description=True, show_default=True)}
    % endif
    % if returns:

**${"Yields:" if returns.is_generator else "Returns:"}**

${table_rows([returns], show_header=True, show_type=True, show_description=True)}
    % endif
    % if raises:
**Raises:**

${table_rows(raises, show_header=True, show_type=True, show_description=True)}
    % endif
% else:
${func.docstring}
% endif

% if show_source_code and func.source:

??? source "View Source"
        ${"\n        ".join(func.source)}

% endif
</%def>


##
## variable()
##

<%def name="variable(var)" buffered="True">
```python3
${var.name}
```
<%
    var_pd = var.parsed_docstring
    if var_pd:
        short_desc = var_pd.short_description
        long_desc = var_pd.long_description
%>
% if var_pd:
${par(short_desc)}
${par(long_desc)}
% else:
${var.docstring}
% endif

</%def>


##
## class()
##

<%def name="class_(cls)" buffered="True">
${h3(cls.name)}

```python3
class ${cls.name}(
    ${",\n    ".join(cls.params())}
)
```
<%
    cls_pd = cls.parsed_docstring
    if cls_pd:
        short_desc = cls_pd.short_description
        long_desc = cls_pd.long_description
        params = cls_pd.params
%>

% if cls_pd:
    % if short_desc:
${short_desc}

    % endif
    %if long_desc:
${long_desc}
    % endif
    % if params:
${h4("Attributes")}

| Name | Type | Description | Default |
|---|---|---|---|
        % for p in params:
| ${p.arg_name} | ${p.type_name} | ${p.description.replace('\n', '<br>')} | ${p.default} |
        % endfor
    % endif
% else:
${cls.docstring}
% endif

% if show_source_code and cls.source:

??? source "View Source"
        ${"\n        ".join(cls.source)}

------

% endif

<%
  class_vars = cls.class_variables()
  static_methods = cls.functions()
  inst_vars = cls.instance_variables()
  methods = cls.methods()
  mro = cls.mro()
  subclasses = cls.subclasses()
%>
% if mro:
${h4('Ancestors (in MRO)')}
    % for c in mro:
* ${c.refname}
    % endfor
% endif

% if subclasses:
${h4('Descendants')}
    % for c in subclasses:
* ${c.refname}
    % endfor
% endif

% if class_vars:
${h4('Class variables')}
    % for v in class_vars:
${variable(v)}

    % endfor
% endif

% if static_methods:
${h4('Static methods')}
    % for f in static_methods:
${function(f, True)}

    % endfor
% endif

% if inst_vars:
${h4('Instance variables')}
% for v in inst_vars:
${variable(v)}

% endfor
% endif
% if methods:
${h4('Methods')}
% for m in methods:
${function(m, True)}

% endfor
% endif

</%def>

###
### Start the output logic for an entire module.
###

<%
  variables = module.variables()
  classes = module.classes()
  functions = module.functions()
  submodules = module.submodules
  heading = 'Namespace' if module.is_namespace else 'Module'
  parsed_ds = module.parsed_docstring
%>

${h1(heading + " " + module.name)}
% if parsed_ds:
${par(parsed_ds.short_description)}
${par(parsed_ds.long_description)}
## TODO: add meta (example and notes)
% else:
${module.docstring}
% endif

${h2("Overview")}

${table_rows(variables, show_header=True, kind='Variable', show_name=True, show_description=True)} \
${table_rows(functions, kind='Function', show_name=True, show_description=True)} \
${table_rows(classes, kind='Class', show_name=True, show_description=True)}

% if show_source_code and module.source:

??? source "View Source"
        ${"\n        ".join(module.source)}

% endif

% if submodules:
${h2("Sub-modules")}
    % for m in submodules:
* [${m.name}](${m.name.split(".")[-1]}/)
    % endfor
% endif

% if variables:
${h2("Variables")}
    % for v in variables:
${variable(v)}

    % endfor
% endif

% if functions:
${h2("Functions")}
    % for f in functions:
${function(f)}

    % endfor
% endif

% if classes:
${h2("Classes")}
    % for c in classes:
${class_(c)}

    % endfor
% endif
