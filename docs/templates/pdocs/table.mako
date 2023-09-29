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
