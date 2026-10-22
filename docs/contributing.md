# Contributing to omnipy development

## Development setup

### Install Python, uv and dependencies

- Make sure that you have Python v3 available from your path. Installation of this depends on your
  local setup. We recommend using `conda`, `pyenv` or `asdf` to manage Python versions. If you are
  using Conda, you can install a Python environment with:

  - `conda create -n omnipy python=3.15`
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
  - `uv run pytest --mypy-pyproject-toml-file=pyproject.toml`

- If you are repeatedly running tests on the command line, e.g.:
  - ```
    export PYTEST_ARGS="--mypy-pyproject-toml-file=pyproject.toml"
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

### Test environment variables

- `OMNIPY_PERSIST_TEST_OUTPUTS=1` stores test cache, job output, and log files in the current
  directory instead of a temporary directory. Use it to inspect files produced by a failing test.

- `OMNIPY_NO_PREFECT_TEST_HARNESS=1` prevents the test suite from starting its own Prefect test
  harness. Set this when connecting tests to an already running Prefect test server.

- `PREFECT_API_URL` gives the URL of that external Prefect API. For example, start a reusable
  local harness in one terminal:
  - `uv run python scripts/start_prefect_test_harness.py`

  Then run tests against it from another terminal:
  - `OMNIPY_NO_PREFECT_TEST_HARNESS=1 PREFECT_API_URL=http://localhost:4200/api uv run pytest --mypy-pyproject-toml-file=pyproject.toml`

## Note on Python type checkers

Omnipy aims to support both `mypy` and `pyright` type checkers. The reason is that `mypy`
is considered the standard type checker in the Python community, but it only works as a static type
checker, while `pyright` can be configured for use in automatic code completion in editors, which is
very useful for development. The `pyright` type checker is also the one that is used by the `vscode`
editor, which is the most popular editor for Python development. The
`PyCharm` editor has its own type checker, which is not advanced enough to handle the typing of
`Omnipy` and therefore (as of Dec 2024) should not be used. Luckily, there is a `pyright` plugin for
`PyCharm` which supports using `pyright` for code completion.

Note: Omnipy has now changed the development setup to use `basedpyright`
instead of `pyright`, but sue of `pyright` is still supported.

From version 2025.3 of PyCharm, support for pyright is included. To set up
just enable Pyright in Settings->Python->Tools->Pyright and specify the path
to the `basedpyright-langserver` binary, e.g. ``.venv/bin/basedpyright-langserver``.

Information on how to configure `pyright` for `JupyterLab` will be added here soon.

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
        `---mypy-pyproject-toml-file=pyproject.toml`
      - Click OK
    - Repeat for other subprojects/test modules as needed, e.g. `pytest in tests.modules` (path=
      `...tests/modules`)

#### For automatic formatting and linting

Formatting, import sorting and linting are handled by [ruff](https://docs.astral.sh/ruff/), configured
in `pyproject.toml`. The formatter follows the Black style, with single quotes and a line length of 100.
Jupyter notebooks are linted and formatted too (source cells only, outputs are left as they are).
`pyproject.toml` and the other TOML files are formatted with
[tombi](https://tombi-toml.github.io/tombi/), configured in `tombi.toml`.

The tools are run as [prek](https://prek.j178.dev) hooks, configured in `prek.toml`. The hooks are
split into two groups: `watch` (docstring macro expansion, ruff, tombi and the whitespace fixers:
fast and suited for running on every file save) and `commit` (the full set, also run by CI).

- To install git hooks that automagically format and lint before every commit:
  - `uv run prek install`

- To run all hooks on all files, as CI does:
  - `uv run prek run --all-files`

- To run only the `watch` hooks on given files:
  - `uv run prek run --group watch --files <file> ...`

- To update the hook repos to their latest versions:
  - `uv run prek update`

- In PyCharm -> File Watchers:
  - Click arrow icon pointing down and to the left
  - Select `pycharm-file-watchers.xml` in the repository root. This adds one watcher that runs
    `prek run --group watch --files $FilePath$` on every file save.
  - Do **not** also enable Settings -> Tools -> Actions on Save -> "Reformat code" for Python:
    PyCharm's built-in formatter follows other style rules than ruff and will fight with it.

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

#### Silence PyCharm's unresolved attribute warnings for models

PyCharm's own type checker cannot follow the typing of `Model[...]`, `Model` subclasses and
`@mimics` models, and infers them as `object`. This gives "Unresolved attribute reference"
warnings in tests, in doctest examples and elsewhere, even though `pyright` and `mypy` accept the
code. To silence them in one place instead of marking individual functions:

- In PyCharm Preferences/Settings->Editor->Inspections->Python->"Unresolved references", add
  `builtins.object.*` to the "Ignored references" list.
  - A quicker way is to press Alt+Enter on one of the warnings and select "Ignore all unresolved
    attributes of builtins.object".

### Configure VS Code for Omnipy

Run `uv sync --all-groups` first, so that the `.venv` and the tools used below exist.

1. Install the extensions: **Python** (`ms-python.python`), **Ruff** (`charliermarsh.ruff`),
   **BasedPyright** (`detachhead.basedpyright`), **Mypy Type Checker**
   (`ms-python.mypy-type-checker`) and a **Tombi** TOML extension (see the
   [Tombi VS Code extension docs](https://tombi-toml.github.io/tombi/docs/editors/vscode-extension)).
2. Select the interpreter: Command Palette -> "Python: Select Interpreter" -> choose
   `.venv/bin/python`.
3. Set Ruff as the default formatter for Python and enable format on save: Settings -> "Default
   Formatter" -> **Ruff** for the Python language, then enable "Editor: Format On Save".
4. Enable Ruff's fix-all and import sorting on save: Settings -> "Code Actions On Save" -> add
   `source.fixAll.ruff` and `source.organizeImports.ruff`, both set to `explicit`.
5. Set Tombi as the default formatter for TOML, with format on save, in the same way as step 3.
6. BasedPyright and the Mypy extension pick up `[tool.basedpyright]` and `[tool.mypy]` from
   `pyproject.toml`.
7. Optionally, run the `watch` hooks on save with the **Run on Save** extension
   (`emeraldwalk.runonsave`), as VS Code has no built-in equivalent of PyCharm's file watchers. Add
   to your `settings.json` (user or workspace, not committed):

   ```json
   "emeraldwalk.runonsave": {
     "commands": [
       {
         "match": ".*",
         "cmd": "uv run prek run --group watch --files ${file}"
       }
     ]
   }
   ```
