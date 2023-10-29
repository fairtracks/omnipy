<%namespace file="general.mako" import="h1, h2, h3, h4, par"/>
<%namespace file="table.mako" import="table_rows"/>
<%namespace file="variable.mako" import="variable"/>
<%namespace file="function.mako" import="function"/>

<%!
    from omnipy.util.mako_helpers import filter_external, filter_internal
%>
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
  class_vars_external = filter_external(cls.class_variables())
  class_vars_internal = filter_internal(cls.class_variables())
  static_methods_external = filter_external(cls.functions())
  static_methods_internal = filter_internal(cls.functions())
  inst_vars_external = filter_external(cls.instance_variables())
  inst_vars_internal = filter_internal(cls.instance_variables())
  methods_external = filter_external(cls.methods())
  methods_internal = filter_internal(cls.methods())
  mro = cls.mro()
  subclasses = cls.subclasses()
%>

## % if mro:
## ${h4('Ancestors (in MRO)')}
##     % for c in mro:
## * ${c.refname}
##     % endfor
## % endif

## % if subclasses:
## ${h4('Descendants')}
##     % for c in subclasses:
## * ${c.refname}
##     % endfor
## % endif

% if class_vars_internal:
${h4('Class variables')}
    % for v in class_vars_internal:
${variable(v)}
    % endfor
% endif

% if static_methods_internal:
${h4('Static methods')}
    % for f in static_methods_internal:
${function(f, True)}
    % endfor
% endif

% if inst_vars_internal:
${h4('Instance variables')}
    % for v in inst_vars_internal:
${variable(v)}
    % endfor
% endif

% if methods_internal:
${h4('Methods')}
    % for m in methods_internal:
${function(m, True)}
    % endfor
% endif

</%def>
