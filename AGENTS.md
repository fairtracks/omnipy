# AGENTS.md

## Tooling

- Use `uv`, not raw `pip`, for normal repo workflows.
- Install dev + docs deps with `uv sync --all-groups`.
- Run repo commands through `uv run ...`.

## Verification

- Full test command: `uv run pytest -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Focused pytest runs still need the same mypy-plugin flags, for example: `uv run pytest tests/components/json/test_json_types.yml --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Check-only formatting/import-order validation matches CI with `uv run pre-commit run --hook-stage manual --all-files`.

## Formatting And Hooks

- Python formatting is `yapf` + `isort`; linting is `flake8`; Python line length is 100 with single quotes.
- Commit-stage pre-commit mutates Python files via `.pre-commit-hooks/expand_docstr_macros.py`. If you edit macro-managed docstrings or `omnipy.util.docstr_macros`, run that hook or expect rewrites.

## Architecture

- Core layout: `src/omnipy/` for library code, `tests/` for mirrored tests plus `integration/`, and `docs/` for user docs.
- `src/omnipy/` is split into `components/` (dataset/task integrations such as json, pandas, prefect), `compute/` (flows, tasks, orchestration primitives), `data/` (core model/dataset machinery), `config/` (config models), `engine/` (execution backends), `hub/` (runtime wiring and UI/log integration), `shared/` (protocols/enums/typedefs), and `util/` (cross-cutting helpers).
- `tests/` broadly mirrors the package structure, with `integration/` separate from faster unit-style areas.
- Most concrete components under `src/omnipy/components/<name>/` use a predictable split across `models.py`, `datasets.py`, `tasks.py`, optional `flows.py`, plus support modules such as `serializers.py`, `helpers.py`, `constants.py`, `typedefs.py`, or `protocols.py`.
- Preserve these naming structures across the repo. If a single-file module becomes too complex, convert it into a same-named package and move the implementation into submodules instead of inventing a new top-level name.
- Tests usually mirror the source package/module path under `tests/`, and filenames often mirror module names (`test_model.py`, `test_dataset.py`, `test_flow.py`, `test_runtime.py`). Common exceptions use behavior-oriented names such as `test_all_engines.py` or `test_serialize_*.py`. Local `conftest.py`, `cases/`, and `helpers/` folders are shared by tests in the same directory.
- Mypy plugin coverage also lives alongside component tests as `.yml` files such as `tests/components/json/test_json_types.yml`.
- `tests/components/conftest.py` autouses `runtime_data_config_variants`, so many component tests run across interactive/non-interactive and dynamic-conversion variants unless they opt out with skip fixtures from `tests/conftest.py`.
- Do not assume every component has a same-named test directory; check `tests/components/**` before adding tests because coverage is not perfectly one-directory-per-component.
- `src/omnipy/__init__.py` is a large public re-export surface. Changes there affect top-level imports and import-time side effects.
- Runtime wiring is centralized in `src/omnipy/hub/runtime.py`: it builds the default runtime on import, wires config subscriptions, and registers both local and Prefect engines.
- Default serializer registration is lazy in `src/omnipy/components/__init__.py`; add/update serializers there if a new dataset type needs automatic registration.

## Test Quirks

- `tests/conftest.py` reorders collection to run ordinary tests first, then `pytest-mypy-plugins` cases, then integration tests.
- During repo tests, `omnipy.hub.runtime.runtime` is intentionally `None`; `src/omnipy/util/helpers.py::called_from_omnipy_tests()` disables the import-time singleton for `tests/...` imports.
- CI installs `de_DE.UTF-8` before running pytest. Reproduce that locale first if locale-sensitive tests fail locally.

## Docs

- User-facing README content is `docs/readme.md`, not a root `README.md`.
- Docs use MkDocs Material. `mkdocs.yml` runs `docs/gen_ref_pages.py` via `mkdocs-gen-files` to generate API reference pages.
- Docs dev server: `uv run mkdocs serve`
