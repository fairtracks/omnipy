#!/usr/bin/env python

# Modified from original code written by GitHub user NeilGirdhar:
# https://github.com/thebjorn/pydeps/issues/40#issuecomment-728280302

# Licensed under the BSD-2-Clause license
#
# Copyright (c) 2014, Bjorn
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pathlib import Path
import subprocess
from typing import Mapping

import typer


def find_modules(path: Path, path_components: list[str]) -> Mapping[str, list[str]]:
    modules: dict[str, list[str]] = {}
    ruined_module = '_'.join(path_components)
    if path.is_dir():
        modules[ruined_module] = (
            path_components[1:] if len(path_components) > 1 else path_components)
        for sub_path in path.iterdir():
            modules.update(find_modules(sub_path, path_components + [sub_path.stem]))
    elif path.is_file() and path.suffix == '.py':
        if path.stem != '__init__':
            modules[ruined_module] = (
                path_components[1:-1] if len(path_components) > 2 else path_components[:-1])
    return modules


def shorten(name: str, modules: Mapping[str, list[str]]) -> str:
    retval = '•'.join(modules[name.strip()])
    if retval in ['graph', 'edge']:
        return f'{retval}_'
    return retval


def attrs(fmt: str) -> dict[str, str]:
    return dict(kv.split('=') for kv in fmt.strip()[:-2].split(','))  # type: ignore


def attrs2fmt(attr_map: Mapping[str, str]) -> str:
    return '[%s];' % ','.join('%s=%s' % (k, v) for k, v in attr_map.items())


def main(base_name: str) -> None:
    modules = find_modules(Path(base_name), [base_name])
    modules = {key: val[0:1] for key, val in modules.items() if '__pycache__' not in key}

    cp = subprocess.run(['pydeps', base_name, '--max-bacon=1', '--show-dot', '--no-output'],
                        stdout=subprocess.PIPE,
                        text=True,
                        check=True)
    lines = cp.stdout.splitlines()
    header = [line for line in lines[:6] if 'concentrate' not in line and line != '']
    body = lines[6:-3]
    nodes = [line for line in body if '->' not in line if line]

    node_mapping: dict[str, dict[str, str]] = {}
    for node in nodes:
        name, fmt = node.split('[')
        sname = shorten(name, modules)
        if sname in node_mapping:
            continue
        node_mapping[sname] = attrs(fmt)

    rules = [line for line in body if '->' in line]

    rule_mapping: dict[tuple[str, str], dict[str, str]] = {}
    used_nodes = set()
    for rule in rules:
        arrow, fmt = rule.split('[')

        a, _, b = arrow.split()
        a = shorten(a, modules)
        b = shorten(b, modules)

        if (a, b) in rule_mapping:
            continue
        if a == b:
            continue
        if b == base_name:
            continue
        rule_mapping[(a, b)] = attrs(fmt)

        used_nodes.add(a)
        used_nodes.add(b)

    with open(f'uml/{base_name}.dot', 'w') as fp:
        fp.write('\n'.join(header))
        for n in used_nodes:
            some_dict: dict[str, str] = node_mapping[n]
            some_dict['label'] = '"%s"' % n
            print('    {} {}'.format(n, attrs2fmt(some_dict)), file=fp)
        for (a, b), fmt_dict in rule_mapping.items():
            print('    {} -> {} {}'.format(a, b, attrs2fmt(fmt_dict)), file=fp)
        print('}', file=fp)

    subprocess.run(['dot', '-Tpng', f'uml/{base_name}.dot', '-o', f'uml/{base_name}.png'])


if __name__ == '__main__':
    typer.run(main)
