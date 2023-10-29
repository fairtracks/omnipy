#!/usr/bin/env python
import pdocs.doc
from portray import api as portray_api


def _is_exported(ident_name):
    return not ident_name.startswith("_") or ident_name in [
        '__enter__',
        '__exit__',
        '__cmp__',
        '__eq__',
        '__getattr__',
        '__setattr__',
        '__getitem_',
        '__setitem__',
        '__delitem__',
        '__iter__',
        '__call__'
    ]


pdocs.doc._is_exported = _is_exported

portray_api.in_browser()
