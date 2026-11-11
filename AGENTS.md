# AGENTS.md

## Tooling

- Use `uv`, not raw `pip`, for normal repo commands.
- Install dev + docs deps with `uv sync --all-groups`.
- Run repo commands through `uv run ...`.

## Verification

- Full test command: `uv run pytest -v --mypy-pyproject-toml-file=pyproject.toml`
- Focused pytest runs still need the same mypy-plugin flags, for example: `uv run pytest tests/components/json/test_json_types.yml --mypy-pyproject-toml-file=pyproject.toml`
- Check-only formatting/lint/import-order validation matches CI with `uv run prek run --all-files`.

## Formatting And Hooks

- TOML files are formatted with `tombi` (`tombi.toml`: line width 100, keys and array items keep their written order).
- Python formatting, import sorting and linting are all handled by `ruff` (`[tool.ruff]` in `pyproject.toml`); Python line length is 100 with single quotes. Import sorting is the `I` lint rule, so it runs under `ruff check --fix`, not `ruff format`.
- The ruff hooks also cover Jupyter notebooks (`docs/notebooks/*.ipynb`): only source cells are linted and formatted, outputs and metadata are left as they are. Notebook cells ignore E501 and F401 (`per-file-ignores`).
- Hooks are run with `prek` (`prek.toml`). Mutating hooks fix files in place, and `prek run` then fails so that CI catches unformatted files. Commit-time hooks mutate Python files via `.pre-commit-hooks/expand_docstr_macros.py`, which runs before the ruff hooks. If you edit macro-managed docstrings or `omnipy.util.docstr_macros`, run that hook or expect rewrites.
- Hooks belong to the groups `watch` (docstring macro expansion, `ruff check --fix`, `ruff format`; fast, for running on every save with `uv run prek run --group watch --files <file>`) and `commit` (the full set, also run by CI).
- The `(str, Enum)` base is used deliberately (not `StrEnum`), and lambda assignment is allowed; both are ignored in the ruff config.
- Avoid unnecessary comments. Use comments to explain complex logic and docstrings to document behavior.

## Layout And Suppression Conventions

Layout: ruff decides. Shape the code instead of overriding the formatter.
- No backslash continuations and no `# fmt: skip/off/on`. When ruff's layout is poor, change the code: put parentheses around the right operand (`assert a == (\n    b\n)`, `x = a or (\n    b\n)`; ruff keeps these but removes redundant parentheses around a whole assertion or right-hand side), move a long trailing comment above the statement, use an intermediate variable, drop an unwanted magic trailing comma, or introduce a type alias (e.g. `AsyncGenCase` in `tests/engine/helpers/classes.py`).
- Ruff keeps a parenthesized *parameter* annotation (`x: (\n    Annotated[...]\n),`) but not a parenthesized return annotation.
- `tests/components/json/cases/json_data.py` and `tests/components/frozen/cases/frozen_data.py` are excluded from `ruff format` (hand-laid-out tables): lay them out with parentheses, never backslashes.
- Pitfalls when running ruff by hand: explicit file paths override `format.exclude` unless `--force-exclude` is given, and `ruff check --select X` replaces the configured rules (use `--extend-select`).

Suppressions:
- Modules that only re-export names list them in `__all__`; do not suppress F401. An import that must follow code gets `# noqa: E402` on the statement.
- File-level directives must name one rule. For names mypy/pyright cannot see, put `# mypy: disable-error-code="attr-defined"` and `# pyright: reportAttributeAccessIssue=false` at the top of the file (mypy rejects a code-qualified module-level `# type: ignore[...]`).
- `# type: ignore[code]` (mypy has `warn_unused_ignores`) and `# pyright: ignore[rule]` must sit on the line where the checker reports the error, which a reformat can move. A pyright-only ignore should be `# pyright: ignore[rule]`. The only `# isort: skip` are the three commented private `typing` imports each in `src/omnipy/shared/typedefs.py` and `src/omnipy/util/helpers.py`.
- `RUF100` rejects `# noqa` comments that suppress nothing. Codes for rules ruff does not implement but PyCharm reads (N806, E731, ARG001, ARG002) are listed in `lint.external`; PyCharm treats every `# noqa` as a general suppression, so those codes are documentation.
- PyCharm infers `Model` instances as `object`. Add `builtins.object.*` to the ignored references of its "Unresolved references" inspection instead of annotating code.

Tests and docs:
- A fixture requested only for its side effects is declared with `@pytest.mark.usefixtures('name')`, not as an unused parameter. This does not work on fixture functions, and a parametrized fixture's part of the test ID changes position.
- Docs examples (`pycon exec` blocks) are run by markdown-exec as a script of the prompt lines: only `print()` output is shown, so display models with `print(x._docs())` in a separate `html="true"` block.

## Typing

- Do not use `cast(object, ...)` / `cast(object, self)` merely to suppress type-checker warnings about suspicious casts. Treat that pattern as a typing escape hatch to avoid in Omnipy code unless explicitly requested.
- Annotate all parameters and return types, also in tests (test functions, fixtures and pytest-cases case functions). Case functions that return several values return a `NamedTuple` or a dataclass with typed fields, created with keyword arguments for readability, which tests take as one argument (e.g. `@pc.parametrize_with_cases('case', cases=...)`).
- Avoid `Any`. Use precise types, protocols or `object` instead.
- Access classmethods and other class attributes through the instance (`model.outer_type()`), not through `type(model)` (`type(model).outer_type()`). Use `type(x)` only where the class itself is needed, e.g. as a type argument (`Dataset[type(model)]`) or to create a new instance.
- The primary static type-checker config is `basedpyright` (`[tool.basedpyright]` in `pyproject.toml`); run it with `uv run basedpyright` when type-checking changes.

## Checking settings and arguments

This is about settings such as config values and the arguments that internal code receives, not about validating data, which is what `Model` is for.

- Check settings where they enter Omnipy, in the config classes (pydantic), not again in the internal code that receives them. Internal classes and functions trust their arguments and do not repeat the checks (e.g. `RequestPacer` relies on `HttpRequestsConfig`).
- Declare constraints as types, so that the internal code shows them too: pydantic's constrained types via `omnipy.util.pydantic` (e.g. `pyd.PositiveInt`, `pyd.PositiveFloat`), and Omnipy's own in `src/omnipy/shared/typedefs.py` (e.g. `ZeroToOneFloat`). Define a new one as a pydantic constrained type with a plain alias under `TYPE_CHECKING`, as pydantic does, so that type checkers accept plain values.
- Test invalid values at the boundary (e.g. `tests/config/`), not in the internal code.

## Architecture

- Core layout: `src/omnipy/` for library code, `tests/` for mirrored tests plus `integration/`, and `docs/` for user docs.
- `src/omnipy/` is split into `components/` (dataset/task integrations such as json, pandas, prefect), `compute/` (flows, tasks, orchestration primitives), `data/` (core model/dataset machinery), `config/` (config models), `engine/` (execution backends), `hub/` (runtime wiring and UI/log integration), `shared/` (protocols/enums/typedefs), and `util/` (cross-cutting helpers).
- `tests/` broadly mirrors the package structure, with `integration/` separate from faster unit-style areas.
- Most concrete components under `src/omnipy/components/<name>/` use a predictable split across `models.py`, `datasets.py`, `tasks.py`, optional `flows.py`, plus support modules such as `serializers.py`, `helpers.py`, `constants.py`, `typedefs.py`, or `protocols.py`.
- Preserve these naming structures across the repo. If a single-file module becomes too complex, convert it into a same-named package and move the implementation into submodules instead of inventing a new top-level name.
- Within Omnipy component code, use relative imports within a component and between components to ease potential extraction into separate repositories. This is an in-Omnipy guideline, not a general import rule for applications or documentation; imports from Omnipy core can use their defining module paths.
- Tests usually mirror the source package/module path under `tests/`, and filenames often mirror module names (`test_model.py`, `test_dataset.py`, `test_flow.py`, `test_runtime.py`). Common exceptions use behavior-oriented names such as `test_all_engines.py` or `test_serialize_*.py`. Local `conftest.py`, `cases/`, and `helpers/` folders are shared by tests in the same directory.
- Mypy plugin coverage also lives alongside component tests as `.yml` files such as `tests/components/json/test_json_types.yml`.
- `tests/components/conftest.py` autouses `runtime_data_config_variants`, so many component tests run across interactive/non-interactive and dynamic-conversion variants unless they opt out with skip fixtures from `tests/conftest.py`.
- Do not assume every component has a same-named test directory; check `tests/components/**` before adding tests because coverage is not perfectly one-directory-per-component.
- `src/omnipy/__init__.py` is a large public re-export surface. Changes there affect top-level imports and import-time side effects.
- Runtime wiring is centralized in `src/omnipy/hub/runtime.py`: it builds the default runtime on import, wires config subscriptions, and registers both local and Prefect engines.
- Default serializer registration is lazy in `src/omnipy/components/__init__.py`; add/update serializers there if a new dataset type needs automatic registration.

## Dataflow Design

- Before designing, implementing, or reviewing an Omnipy dataflow, read the
  repository's [omnipy-dataflows skill](.agents/skills/omnipy-dataflows/SKILL.md).
  It applies across domains, including application flows, component flows, and
  narrative integration examples.
- Prefer typed models and datasets, model-based validation/conversion, and
  reusable task/flow composition. The skill explains when other structures fit,
  and documents the routing and async details needed to use these defaults.
- Make model and flow declarations readable as an inspectable contract for the
  agent's output. Narrative integration tests also serve as tutorials: design
  their implementations for reuse in documentation and show Omnipy's declarative
  composition, mimicking Models, and Dataset batch operations clearly.
- For exhaustive engine/callable behavior tests, keep using the existing engine
  harness; a domain scenario should remain a readable proof of a real dataflow.

## Test Organization

- Put reusable pytest-cases case functions in a sibling `cases/` package, not in `helpers/`.
- Split `cases/` modules by topic or function, especially when cases are reused across test modules.
- Put reusable helper classes in adjacent `helpers/classes.py` modules and helper functions in `helpers/functions.py`.
- Keep test modules focused on assertions and wiring; move reusable setup data and helper types out.
- Prefer `pytest_cases.parametrize_with_cases()` for shared case data instead of duplicating inline parametrization.

## Test Quirks

- `tests/conftest.py` reorders collection to run ordinary tests first, then `pytest-mypy-plugins` cases, then integration tests.
- During repo tests, `omnipy.hub.runtime.runtime` is intentionally `None`; `tests/conftest.py:pytest_configure()` disables the import-time singleton for `tests/...` imports. It also resets the shared data class and job creators, which building that runtime configured for the detected environment (e.g. the terminal color system), so tests do not depend on the terminal or on test order.
- CI installs `de_DE.UTF-8` before running pytest. Reproduce that locale first if locale-sensitive tests fail locally.

## Commit Messages

- Describe concrete technical changes. Include intent only when it explains specific technical reasons, not general improvements.
- Do not use the word "refactor" when functional changes are made.
- Name the main public classes or functions affected when one or two are central to the change. For private implementation details, name the nearest affected public class or function instead.
- Separate distinct changes with periods rather than commas.
- Several small changes can be summarized as "cleanup", "misc fixes", or "typing improvements".

For example: "Cleanup ConfigBase display methods. Misc fixes in BaseDisplayMixin."

## Working Documents

- Plans, specs, reviews and other working documents written by agents go under `docs/agents/`, filed as described in `docs/agents/README.md` (e.g. `docs/agents/technical/plans/` and `docs/agents/technical/specs/`, with a date prefix in the filename).
- This location overrides the ones that skills or plugins define for such documents, such as `docs/superpowers/plans/` and `docs/superpowers/specs/` from the superpowers skills.
- `docs/agents/` is excluded from the MkDocs site, and the plans and specs under `docs/agents/technical/` are excluded from `ruff format`, so they are kept as written.

## Docs

- User-facing README content is written in `docs/readme.md`, the MkDocs home page, whose examples run when the docs are built. The root `README.md` (shown by GitHub and PyPI) and `docs/images/readme/*.svg` are generated from it: after editing `docs/readme.md`, run `uv run python docs/gen_readme.py` and commit the results. `hatch_build.py` rewrites the image links to raw GitHub URLs of the release tag when the package is built, so PyPI shows the images of the released version.
- Docs use MkDocs Material. `mkdocs.yml` runs `docs/gen_ref_pages.py` via `mkdocs-gen-files` to generate API reference pages.
- Docs dev server: `uv run mkdocs serve`

## Documentation examples conventions

Code examples in docs/ pages follow these rules:

- **Imports**: Use `import omnipy as om` and `import pydantic as pyd` as the default.
  Reference types as `om.Model`, `pyd.BaseModel`, etc.
  When the `om.` prefix creates visual clutter (e.g. using both Model and Dataset
  repeatedly in one block), add `from omnipy import Dataset, Model` — limit
  explicit imports to at most these two names.

- **No setup/config bloat**: Unless configuration IS the example's topic, hide
  runtime setup (e.g. `runtime.config.data.model.interactive = False`) behind
  markdown-exec setup blocks so the reader sees only relevant code and output.

- **Display output**: Use `._docs()` as the default and, in addition, `.content`
  to show stored data if there is a particular need for that. Use `.peek(debug=True)` only for in-depth technical
  explanations of model internals. Avoid `.to_data()` unless documenting that
  method itself.
