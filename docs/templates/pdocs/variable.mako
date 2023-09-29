<%namespace file="general.mako" import="h1, h2, h3, h4, par"/>
<%namespace file="table.mako" import="table_rows"/>

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