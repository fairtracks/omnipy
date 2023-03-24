import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Omnipy'
copyright = '2023, Sveinung Gundersen, Joshua Baskaran, Federico Bianchini, Jeanne Cheneby, Ahmed Ghanem, Pável Vázquez'
author = 'Sveinung Gundersen, Joshua Baskaran, Federico Bianchini, Jeanne Cheneby, Ahmed Ghanem, Pável Vázquez'
release = '0.10.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
]

autoapi_dirs = ['../../src/omnipy']
autoapi_keep_files = False
autoapi_type = 'python'
autoapi_template_dir = '../templates/autoapi'
autoapi_options = [
    'members',
    'inherited-members',
    'undoc-members',
    'special-members',
    'show-inheritance',
    'show-module-summary',
    'imported-members',
]

autodoc_typehints = 'signature'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'
html_static_path = ['../static']

toc_object_entries = False


def attr_inherited_from_other_package(attr_name_rel: str, class_name: str, module_abs: str) -> bool:
    import importlib
    import inspect

    try:
        module = importlib.import_module(module_abs)
        cls = getattr(module, class_name)

        attr_info = None
        for attr in inspect.classify_class_attrs(cls):
            if attr.name == attr_name_rel:
                attr_info = attr

        return attr_info is None or attr_info.defining_class.__module__.split('.')[0] != 'omnipy'
    except Exception as e:
        print(f'Exception occurred for attr {attr_name_rel}: {type(e)} {e}')
        return True


def skip_members(app, what, name, obj, skip, options):
    name_split = name.split('.')
    name_rel = name_split[-1]

    if what in ('method', 'attribute'):
        assert len(name_split) > 3, name
        class_name = name_split[-2]
        module_abs = '.'.join(name_split[:-2])

        if name_rel.startswith('__'):
            # __call__ method of Template classes are internal, should not be used externally
            if name_rel != '__call__' or class_name.endswith('Template'):
                skip = True
        elif attr_inherited_from_other_package(name_rel, class_name, module_abs):
            skip = True

    elif what == 'class' and name_rel in ('Config', 'list', 'dict'):
        skip = True

    return skip


def setup(sphinx):
    sphinx.connect('autoapi-skip-member', skip_members)


sys.path.insert(0, os.path.abspath('../src'))

# Copied from https://github.com/abey79/vsketch/blob/master/docs/conf.py under the following
# license:
#
# ------------------------------
# MIT License
#
# Copyright (c) 2020 Antoine Beyeler & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def contains(seq, item):
    """Jinja2 custom test to check existence in a container.
    Example of use:
    {% set class_methods = methods|selectattr("properties", "contains", "classmethod") %}
    Related doc: https://jinja.palletsprojects.com/en/3.1.x/api/#custom-tests
    """
    return item in seq


def prepare_jinja_env(jinja_env) -> None:
    """Add `contains` custom test to Jinja environment."""
    jinja_env.tests['contains'] = contains


autoapi_prepare_jinja_env = prepare_jinja_env

# Custom role for labels used in auto_summary() tables.
rst_prolog = """
.. role:: summarylabel
"""

# Related custom CSS
html_css_files = ['css/label.css']
