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
autoapi_keep_files = False
autoapi_type = "python"
autoapi_template_dir = "templates/autoapi"
autoapi_options = [
    "members",
    "inherited-members",
    "undoc-members",
    "special-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]

autodoc_typehints = "both"


def skip_members(app, what, name, obj, skip, options):
    if what in ("method", "attribute") and name.split('.')[-1].startswith('__'):
        skip = name not in ('__call__',)
    return skip


def setup(sphinx):
    sphinx.connect("autoapi-skip-member", skip_members)


# templates_path = ['templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
# html_static_path = ['_static']

sys.path.insert(0, os.path.abspath('../src'))
