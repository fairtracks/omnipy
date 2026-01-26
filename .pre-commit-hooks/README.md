# Custom Pre-commit Hooks

## Docstring Macro Expander

The `copy_docstrings.py` hook maintains DRY documentation by expanding reusable docstring macros defined via **environment variables**. Original docstrings (with unexpanded macros) are preserved in comments immediately before expanded docstrings, allowing re-expansion when macro definitions change.

### Key Features

- **Environment-based**: Macros defined purely through environment variables (no config files)
- **DRY**: Define common docstring patterns once, use everywhere
- **Idempotent**: Re-run to update all expansions when macros change
- **Source-level**: Original docstrings with macros stored as comments in your code
- **Testable**: Core logic in `omnipy.util.docstr_macros` with pytest tests

### Usage

#### 1. Define macros via environment variables

```bash
export OMNIPY_MACRO_COMMON_PARAM='Parameters:
    param1 (str): The first parameter
    param2 (int): The second parameter'

export OMNIPY_MACRO_COMMON_RETURN='Returns:
    dict: A dictionary containing the results'
```

The environment variable `OMNIPY_MACRO_COMMON_PARAM` defines the macro `{{COMMON_PARAM}}`.

#### 2. Use macros in your docstrings

```python
def example_method(self):
    """Example method with custom text.
    
    This method does something special.
    
    {{COMMON_PARAM}}
    {{COMMON_RETURN}}
    
    Note: Remember this!
    """
    return {}
```

#### 3. Run the hook

```bash
python .pre-commit-hooks/copy_docstrings.py --verbose path/to/file.py
```

### Testing

```bash
export OMNIPY_MACRO_TEST='Test value'
pytest tests/util/test_docstr_macros.py -v
```
