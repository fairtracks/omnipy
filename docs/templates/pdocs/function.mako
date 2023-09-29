<%namespace file="general.mako" import="h1, h2, h3, h4, par"/>
<%namespace file="table.mako" import="table_rows"/>

<%!
    from docstring_parser import DocstringParam, DocstringReturns
    from omnipy.util.mako_helpers import get_type_name_from_annotation
%>

<%!
    IGNORED = None
    IGNORE_PARAMS = ['cls', 'self']
%>
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
