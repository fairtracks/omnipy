<%namespace file="general.mako" import="h1, h2, h3, h4, par"/>
<%namespace file="table.mako" import="table_rows"/>
<%namespace file="variable.mako" import="variable"/>
<%namespace file="function.mako" import="function"/>
<%namespace file="class.mako" import="class_"/>

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
