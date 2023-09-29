<%namespace file="general.mako" import="h1, h2, h3, h4, par"/>
<%namespace file="table.mako" import="table_rows"/>
<%namespace file="variable.mako" import="variable"/>
<%namespace file="function.mako" import="function"/>

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