# AGENTS.md

## Tooling

- Use `uv`, not raw `pip`, for normal repo workflows.
- Install dev + docs deps with `uv sync --all-groups`.
- Run repo commands through `uv run ...`.

## Verification

- Full test command matches CI: `uv run pytest -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Focused tests still need the same mypy-plugin flags, for example: `uv run pytest tests/components/json/test_json_types.yml --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- CI also runs `pre-commit run --hook-stage manual --all-files`; use that for check-only formatting/import-order validation.

## Formatting And Hooks

- Python formatting is `yapf` + `isort`; linting is `flake8`. Line length is 100, and `.editorconfig` sets single quotes.
- Pre-commit on the normal commit stage mutates Python files: `expand_docstr_macros` rewrites docstrings from `OMNIPY_MACRO_*` environment variables via `.pre-commit-hooks/expand_docstr_macros.py`.
- If you edit macro-managed docstrings or `omnipy.util.docstr_macros`, run that hook or expect pre-commit to rewrite files.

## Architecture

- All package code lives under `src/omnipy`; tests live under `tests` with major areas such as `components`, `data`, `compute`, `engine`, `integration`, and `util`.
- `src/omnipy/__init__.py` is the public API surface and re-exports a very large share of the library. Changes there affect top-level imports and import-time behavior.
- Runtime wiring is centralized in `src/omnipy/hub/runtime.py`: it creates the default runtime on import, wires config to objects, and registers both local and Prefect engines.
- Core flow/engine behavior is split across `src/omnipy/compute/flow.py`, `src/omnipy/engine/local.py`, and `src/omnipy/components/prefect/engine/prefect.py`.
- Serializer registration is lazy in `src/omnipy/components/__init__.py`; add/update serializers there if a new dataset type needs default registration.

## Test Quirks

- `tests/conftest.py` reorders collection to run ordinary tests first, then `pytest-mypy-plugins` cases, then integration tests. Do not assume pytest's default order when comparing output.
- The global `runtime` singleton is intentionally disabled during repo tests: `called_from_omnipy_tests()` makes `omnipy.hub.runtime.runtime` be `None` under `tests/...` imports.
- CI installs `de_DE.UTF-8` before running pytest. If locale-sensitive tests fail locally, reproduce that locale first.

## Docs

- User-facing README content is `docs/readme.md`, not a root `README.md`.
- Docs are MkDocs Material (`mkdocs.yml`) and reference pages are generated from `docs/gen_ref_pages.py`.
- Docs dev server: `uv run mkdocs serve`
