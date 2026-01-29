"""
Tests for docstring macro expansion.

Authors:
    - Sveinung Gundersen (concept, requirements, review and refactoring)
    - GitHub Copilot w/ Claude Sonnet 4.5 (impl. assistance, January 2026)

Created: January 2026
"""

import os
from textwrap import dedent

import pytest

from omnipy.util.docstr_macros import (expand_macros,
                                       find_macros_in_docstring,
                                       get_macros_from_env,
                                       process_content)


@pytest.fixture
def sample_macros() -> dict[str, str]:
    """Provide sample macro definitions for testing."""
    return {
        'COMMON_PARAM':
            dedent("""\
            Args:
                param1 (str): First parameter
                param2 (int): Second parameter"""),
        'COMMON_RETURN':
            dedent("""\
            Returns:
                dict: A dictionary result"""),
        'EXAMPLE':
            dedent("""\
            Example:
                >>> obj.method()
                result"""),
    }


def test_get_macros_from_env() -> None:
    """Test loading macros from environment variables."""
    # Set up test environment variables
    os.environ['OMNIPY_MACRO_TEST1'] = 'Value 1'
    os.environ['OMNIPY_MACRO_TEST2'] = 'Value 2'
    os.environ['OTHER_VAR'] = 'Should be ignored'

    try:
        macros = get_macros_from_env()

        assert 'TEST1' in macros
        assert 'TEST2' in macros
        assert macros['TEST1'] == 'Value 1'
        assert macros['TEST2'] == 'Value 2'
        assert 'OTHER_VAR' not in macros
    finally:
        # Clean up
        del os.environ['OMNIPY_MACRO_TEST1']
        del os.environ['OMNIPY_MACRO_TEST2']
        del os.environ['OTHER_VAR']


def test_find_macros_in_docstring(sample_macros) -> None:
    """Test finding macros in docstrings."""
    docstring = dedent("""\
        My function.

        {{COMMON_PARAM}}

        {{COMMON_RETURN}}""")
    found = find_macros_in_docstring(docstring, sample_macros)
    assert found == {'COMMON_PARAM', 'COMMON_RETURN'}


def test_find_no_macros(sample_macros) -> None:
    """Test when no macros are present."""
    docstring = 'Simple docstring with no macros.'
    found = find_macros_in_docstring(docstring, sample_macros)
    assert found == set()


def test_expand_macros(sample_macros) -> None:
    """Test expanding macros in text."""
    text = dedent("""\
        My function.

        {{COMMON_PARAM}}""")
    expanded = expand_macros(text, sample_macros)
    assert '{{COMMON_PARAM}}' not in expanded
    assert '    param1 (str): First parameter' in expanded


def test_expand_multiple_macros(sample_macros) -> None:
    """Test expanding multiple macros."""
    text = dedent("""\
        {{COMMON_PARAM}}

        {{COMMON_RETURN}}""")
    expanded = expand_macros(text, sample_macros)
    assert '{{COMMON_PARAM}}' not in expanded
    assert '{{COMMON_RETURN}}' not in expanded
    assert '    param1 (str)' in expanded
    assert '    dict: A dictionary result' in expanded


def test_expand_multiple_macros_manage_indentation(sample_macros) -> None:
    """Test expanding multiple macros."""
    text = dedent("""\
        {{COMMON_PARAM}}

            {{COMMON_RETURN}}""")
    expanded = expand_macros(text, sample_macros)
    assert '{{COMMON_PARAM}}' not in expanded
    assert '{{COMMON_RETURN}}' not in expanded
    assert '    param1 (str)' in expanded
    assert '        dict: A dictionary result' in expanded


def test_process_content_first_expansion(sample_macros) -> None:
    """Test first-time macro expansion in content."""
    source = dedent('''\
        def my_function():
            """
            My function.

            {{COMMON_PARAM}}
            """
            pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert modified

    assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    #
    # My function.
    #
    # {{COMMON_PARAM}}
    #
    """''' in result  # Note: first and last lines are empty to denote line breaks at ends

    assert '''\
    """
    My function.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter
    """''' in result


def test_process_content_first_expansion_no_whitespace_at_ends_of_docstr(sample_macros) -> None:
    """Test first-time macro expansion in content."""
    source = dedent('''\
        def my_function():
            """My function.

            {{COMMON_PARAM}}"""
            pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert modified

    assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    # My function.
    #
    # {{COMMON_PARAM}}
    """''' in result  # Note: first and last lines are not empty as there are no line breaks at ends

    assert '''\
    """My function.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter"""''' in result


def test_process_content_no_macros(sample_macros) -> None:
    """Test content without macros is unchanged."""
    source = dedent('''\
        def my_function():
            """Simple docstring."""
            pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert not modified
    assert result == source


def test_process_content_reexpansion(sample_macros) -> None:
    """Test re-expansion when macro definition changes."""
    # Content that's already been processed
    source = dedent('''\
        def my_function():
            # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
            #
            # My function.
            # {{COMMON_PARAM}}
            #
            """
            My function.
            Args:
                param1 (str): OLD VALUE
            """
            pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert modified

    assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    #
    # My function.
    # {{COMMON_PARAM}}
    #
    """''' in result  # Ensure original comment block is preserved exactly

    assert '''\
    """
    My function.
    Args:
        param1 (str): First parameter
        param2 (int): Second parameter
    """\n''' in result  # Ensure docstring is exactly as before except for expansion


def test_process_content_reexpansion_no_whitespace_at_ends_of_docstr(sample_macros) -> None:
    """Test re-expansion when macro definition changes."""
    # Content that's already been processed
    source = dedent('''\
        def my_function():
            # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
            # My function.
            #
            # This is my function.
            #
            # {{COMMON_PARAM}}
            """My function.

            This is my function.

            Args:
                param1 (str): OLD VALUE"""
            pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert modified

    assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    # My function.
    #
    # This is my function.
    #
    # {{COMMON_PARAM}}
    """''' in result  # Ensure original comment block is preserved exactly

    assert '''\
    """My function.

    This is my function.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter"""\n''' in result


def test_process_content_mixed_text_and_macros_repeated(sample_macros) -> None:
    """Test docstring with custom text mixed with macros."""
    source = dedent('''\
        def my_function():
            """My custom function.

            This does something special.

            {{COMMON_PARAM}}

            Returns:
                Not sure what.
            """
            pass
        ''')

    for i in range(2):
        result, modified = process_content(source, sample_macros)

        assert modified

        assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    # My custom function.
    #
    # This does something special.
    #
    # {{COMMON_PARAM}}
    #
    # Returns:
    #     Not sure what.
    #
    """''' in result

        assert '''\
    """My custom function.

    This does something special.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter

    Returns:
        Not sure what.
    """\n''' in result

        source = result


def test_process_content_class_docstring(sample_macros) -> None:
    """Test macro expansion in class docstrings."""
    source = dedent('''\
        class MyClass:
            """My class.

            {{COMMON_PARAM}}
            """
            pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert modified

    assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    # My class.
    #
    # {{COMMON_PARAM}}
    #
    """''' in result

    assert '''\
    """My class.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter
    """\n''' in result


def test_process_content_multiple_docstrings(sample_macros) -> None:
    """Test processing multiple docstrings in same file."""
    source = dedent('''\
        class MyClass:
            """Class docstring.

            {{COMMON_PARAM}}
            """

            def method(self):
                """Method docstring.

                {{COMMON_RETURN}}
                """
                pass
        ''')

    result, modified = process_content(source, sample_macros)

    assert modified

    assert '''\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    # Class docstring.
    #
    # {{COMMON_PARAM}}
    #
    """''' in result

    assert '''\
    """Class docstring.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter
    """\n''' in result

    assert '''\
        # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
        # Method docstring.
        #
        # {{COMMON_RETURN}}
        #
        """''' in result  # Correct indentation for method

    assert '''\
        """Method docstring.

        Returns:
            dict: A dictionary result
        """\n''' in result  # Correct indentation for method


def test_process_content_empty_string(sample_macros) -> None:
    """Test processing empty content."""
    result, modified = process_content('', sample_macros)

    assert not modified
    assert result == ''


def test_process_content_triple_single_quotes(sample_macros) -> None:
    """Test with triple single quote docstrings."""
    source = dedent("""\
        def my_function():
            '''My function.

            {{COMMON_PARAM}}
            '''
            pass
        """)

    result, modified = process_content(source, sample_macros)

    assert modified

    assert """\
    # %% Original docstring with macros (managed by expand_docstring_macros.py) %%
    # My function.
    #
    # {{COMMON_PARAM}}
    #
    '''""" in result

    assert """\
    '''My function.

    Args:
        param1 (str): First parameter
        param2 (int): Second parameter
    '''\n""" in result
