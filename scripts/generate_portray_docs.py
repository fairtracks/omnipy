#!/usr/bin/env python
from enum import Enum
import os

import pdocs.doc
from portray import api as portray_api
import typer


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


class Command(str, Enum):
    IN_BROWSER = 'in_browser'
    AS_HTML = 'as_html'
    FOR_READTHEDOCS = 'for_readthedocs'
    # ON_GITHUB_PAGES = 'on_github_pages'


def main(cmd: Command):
    if cmd == Command.IN_BROWSER:
        portray_api.in_browser()
    if cmd == Command.AS_HTML:
        portray_api.as_html()
    if cmd == Command.FOR_READTHEDOCS:
        readthedocs_path = os.getenv('READTHEDOCS_OUTPUT', '')
        if readthedocs_path:
            readthedocs_path += os.path.sep
        readthedocs_path += 'html'
        if not os.path.exists(readthedocs_path):
            os.makedirs(readthedocs_path)
        portray_api.as_html(output_dir=readthedocs_path, overwrite=True)
    # elif cmd == Command.ON_GITHUB_PAGES:
    #     portray_api.on_github_pages()


if __name__ == '__main__':
    typer.run(main)
