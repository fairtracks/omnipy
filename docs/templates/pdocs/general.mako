##
## Disable omnipy root log formatter
##

<%!
    from omnipy import runtime
    runtime.config.root_log.log_format_str = None
%>

##
## Constants
##

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
