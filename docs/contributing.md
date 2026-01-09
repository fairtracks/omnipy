# Contributing to omnipy development

## Development setup

### Install Python, uv and dependencies

- Make sure that you have Python v3 available from your path. Installation of this depends on your
  local setup. We recommend using `conda`, `pyenv` or `asdf` to manage Python versions. If you are 
  using Conda, you can install a Python environment with:

  - `conda create -n omnipy python=3.10`
  - `conda activate omnipy`

- Install uv:
  - `curl -LsSf https://astral.sh/uv/install.sh | sh`

- Install dependencies:
  - `uv sync --all-groups`

### uv commands

#### Installing dependencies

- Install all dependencies (including all groups):
  - `uv sync --all-groups`

- Install only main dependencies:
  - `uv sync`

- Install specific dependency groups:
  - `uv sync --group dev`
  - `uv sync --group docs`

#### Updating dependencies

- Update all dependencies:
  - `uv lock --upgrade`

- Update single dependency, e.g.:
  - `uv lock --upgrade-package prefect`


- If a dependency is not updated to the latest version available on Pypi,
  you might need to clear the cache:
  - `uv cache clean`

#### Running commands

- Run any command in the virtual environment:
  - `uv run <command>`
  - Examples:
    - `uv run pytest`
    - `uv run python script.py`
    - `uv run mkdocs serve`

#### Building and publishing

- Build the package:
  - `uv build`

- Install in editable mode:
  - `uv pip install -e .`

### Running tests

- To run all tests, type:
  - `uv run pytest --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`

- If you are repeatedly running tests on the command line, e.g.:
  - ```
    export PYTEST_ARGS="--mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process"
    ```
  - Using `zsh`, which is default shell on Mac:
    - `uv run pytest $=PYTEST_ARGS tests`
  - Using `bash`:
    - `eval uv run pytest $PYTEST_ARGS tests`

- With a specific subpackage/testmodule
  - Using `zsh`:
    - `uv run pytest $=PYTEST_ARGS tests/modules/json`
  - Using `bash`:
    - `eval uv run pytest $PYTEST_ARGS tests/modules/json`

- With a specific test module (this test example is a mypy typing test, which is the reason for the
  extra variables in the first place):
  - Using `zsh`:
    - `uv run pytest $=PYTEST_ARGS tests/modules/json/test_json_types.yml`
  - Using `bash`:
    - `eval uv run pytest $PYTEST_ARGS tests/modules/json/test_json_types.yml`

- With a specific test:
  - Using `zsh`:
    - `uv run pytest $=PYTEST_ARGS tests/modules/json/test_json_types.yml::test_json_scalar`
  - Using `bash`:
    - `eval uv run pytest $PYTEST_ARGS tests/modules/json/test_json_types.yml::test_json_scalar`

## Note on Python type checkers

Omnipy aims to support both `mypy` and `pyright` type checkers. The reason is that `mypy`
is considered the standard type checker in the Python community, but it only works as a static type
checker, while `pyright` can be configured for use in automatic code completion in editors, which is
very useful for development. The `pyright` type checker is also the one that is used by the `vscode`
editor, which is the most popular editor for Python development. The
`PyCharm` editor has its own type checker, which is not advanced enough to handle the typing of
`Omnipy` and therefore (as of Dec 2024) should not be used. Luckily, there is a `pyright` plugin for
`PyCharm` which supports using `pyright` for code completion.

Information on how to configure `pyright` for `PyCharm` and `JupyterLab` will be added here soon.

### Configure PyCharm project for Omnipy

- Preparation (in terminal). Note the path to the Python binary:
  - `which python`

- In Setting/Preferences dialog:
  - Select Project Interpreter (under Project: omnipy)
    - Click "Add interpreter" -> "Add Local Interpreter"
    - Select "Existing environment"
    - Select "uv"
    - Make sure that the `.venv/bin/python` binary in your project directory is selected
    - Click "OK"

  - Select "Project structure"
    - Make sure that the "src" directory is selected under "Source Folders"

  - Under "Editor" -> "File Types", select the tab "Ignored Files and Folders"
    - Click the "+" button
      - Type ".venv"
    - Type Enter

  - Click "OK" to save new settings

#### Setting up test configurations

- From Run menu (in menubar) or configuration popup (by the triangle icon):
  - Select "Edit Configurations..."
    - Click "+" to add new configuration, select "Python tests"->"pytest"
      - Name: `pytest in tests`
      - Script path: select "tests" directory
      - Additional arguments:
        `--mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
      - Click OK
    - Repeat for other subprojects/test modules as needed, e.g. `pytest in tests.modules` (path=
      `...tests/modules`)

#### For automatic formatting and linting

The setup for automatic formatting and linting is rather complex. The main alternative is to use
black, which is easier to set up, but it does not have as many options and the main omnipy developer
is opinionated against the default black setup. The yapf config is not fully defined.

- To install git hooks that automagically format and lint before every commit:
  - `pre-commit install`

- To update pre-commit-managed dependencies to the latest repos' versions:
  - `pre-commit autoupdate`

- In PyCharm -> File Watchers:
  - Click arrow icon pointing down and to the left
  - Select `pycharm_file_watchers.xml`

#### Recommended Pycharm plugins

- Install the following plugins:
  - File Expander (to view compressed files as a folder structure)
  - CSV Editor (to edit CSV files as tables. Only needed in Community edition of PyCharm, similar
    functionality is included in the Professional version)

#### For mypy support in PyCharm

- In PyCharm, install "Mypy" plugin (not "Mypy (Official)")
  - `which mypy` to get path to mypy binary
  - In the PyCharm settings for the mypy plugin:
    - Select the mypy binary
    - Select `pyproject.toml` as the mypy config file
- In PyCharm Preferences/Settings->Editor->Inspections, uncheck the following:
  - "Incorrect type"
  - "Invalid type hints definitions and usages"
  - "Missing type hinting for function definition"
