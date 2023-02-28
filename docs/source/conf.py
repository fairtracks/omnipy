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
release = '0.9.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
]

autoapi_dirs = ['../../src/omnipy']
autoapi_keep_files = True
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


# templates_path = ['templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
# html_static_path = ['_static']

sys.path.insert(0, os.path.abspath('../src'))
