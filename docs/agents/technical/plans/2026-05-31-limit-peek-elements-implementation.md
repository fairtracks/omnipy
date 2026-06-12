# Limit Peek Elements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe, fail-open preview pruning for bounded-height model and dataset previews, including `width=None, height bounded` paths, plus bounded-row `Dataset.list()` materialization, without changing public APIs or renderer-owned output behavior.

**Architecture:** Introduce an internal `preview_pruning.py` helper that decides whether a `DraftPanel` can be safely front-pruned before expensive pretty-printer preparation. The helper is wired into `pretty.py`, chooses one active chunking path at a time using cheap metadata, uses bounded heuristic probe renders under the real assigned panel frame, and must fail open whenever bounded-height safety or probe stability cannot be established. `Dataset.list()` remains a separate optimization in `display.py`, limiting row work to the visible range plus a small safety margin.

**Tech Stack:** Python, existing Omnipy display/layout/pretty-printer stack, `pytest`, `uv`, `pre-commit`

---

## Implementation authority

- Revised spec: `docs/agents/technical/specs/2026-05-19-limit-peek-elements-design.md`
- This plan intentionally stays high-level. The implementation worker should use TDD to refine the exact helper interfaces from the tests.

## Files in scope

- Create: `src/omnipy/data/_display/text/preview_pruning.py`
- Modify: `src/omnipy/data/_display/text/pretty.py`
- Modify: `src/omnipy/data/_mixins/display.py`
- Create: `tests/data/display/text/test_preview_pruning.py`
- Modify: `tests/data/display/text/test_pretty.py`
- Modify: `tests/data/test_model.py`
- Modify: `tests/data/test_dataset.py`

## Constraints and non-goals

- No public API changes and no new public kwargs.
- No ellipsis insertion in the pruner.
- For v1 general containers, pruning is gated to bounded-height cases only: `width=None, height bounded` may prune, while `height=None` must skip pruning regardless of width.
- If width stabilization is used and does not stabilize before the probe cap, pruning must fail open to the full unpruned content.
- Coarse-ness and path-selection checks must use cheap metadata only; they must not force expensive chunk construction, full `splitlines()`, `list(mapping.items())`, deep traversal, or `to_data()`-style conversion solely to pick a pruning level.
- Keep the current exponential-growth plus binary-search refinement strategy; this slice does not add a separate binary-search cap parameter.
- Probe budgets should use the title-adjusted content viewport (`inner_frame.dims`), not raw outer frame dimensions.
- `Dataset.list()` should not add extra width compensation logic for hidden rows; the current implementation does not require it.
- Avoid changing `DraftPanel`, `Layout`, `PanelDesignDims`, or `render_next_stage()` unless a test proves that the spec cannot be met otherwise.

## Primary acceptance contracts

Tests are the primary deliverable for this plan.

- Bounded-height safe cases: rendering a pruned prefix yields the same visible viewport as rendering the full content and cropping to the viewport.
- `width=None, height bounded` previews may prune; `height=None` previews must fall back to current full-content behavior.
- Unsafe or inconclusive cases: probe instability, recursion/cycle issues, path-selection ambiguity, unavailable cheap metadata, and probe errors all fall back to current full-content behavior.
- `peek()`, `json()`, and `full()` keep current public semantics; only the internal amount of prepared content changes where safely allowed.
- `Dataset.list()` materializes only visible rows plus a small safety margin while preserving current visible output.
- Top-level dataset panel limiting remains intact; child-panel pruning is still per-panel and frame-local.

## Planned verification commands

- Focused unit tests:
  - `uv run pytest tests/data/display/text/test_preview_pruning.py --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Focused display/integration tests:
  - `uv run pytest tests/data/display/text/test_pretty.py tests/data/test_model.py tests/data/test_dataset.py --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Broader verification:
  - `uv run pytest -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
- Formatting/import/lint gate:
  - `uv run pre-commit run --hook-stage manual --all-files`

## Known risks

- Width-sensitive pretty-printers can reflow earlier visible output based on later items; this is why bounded-height gating, cheap path selection, and fail-open behavior are the core correctness guardrails.
- Probe rendering can accidentally recurse back into pruning unless the probe path is explicitly isolated.
- Memoization must stay scoped to a single top-level render call; broader caching risks stale or cross-frame results.
- Hierarchical path selection must not introduce holes or silently switch among sibling subtrees; restart-on-promotion behavior is the main guardrail here.
- `Dataset.list()` optimization must reduce work without changing the currently visible table output or row numbering.

### Task 0: Characterize current `peek()` and `list()` behavior

**Purpose:** Freeze current externally visible behavior before optimization work starts.

**Files:**
- Modify: `tests/data/display/text/test_pretty.py`
- Modify: `tests/data/test_model.py`
- Modify: `tests/data/test_dataset.py`

- [ ] Add characterization tests that pin down current viewport behavior for representative `peek()`, `json()`, and `full()` cases under bounded and unbounded dimensions, including `width=None, height bounded` and `height=None` cases.
- [ ] Add characterization coverage for `Dataset.list()` framing and row presentation so later optimization can be proven non-behavior-changing.
- [ ] Run the focused display/integration tests and confirm the baseline is green before introducing pruning logic.

**Acceptance focus:** Current behavior is documented in tests before any new helper logic exists.

**User Check-in:** Confirm the characterization suite covers the intended external contracts before moving into the new pruning helper.

### Task 1: Add `preview_pruning.py` helper module with unit tests

**Purpose:** Establish the pruning contract in isolation, driven by tests before wiring it into production call paths.

**Files:**
- Create: `src/omnipy/data/_display/text/preview_pruning.py`
- Create: `tests/data/display/text/test_preview_pruning.py`

- [ ] Add failing unit tests that define safe gating, prefix selection, chunking behavior, probe caps, memoization scope, and fail-open outcomes.
- [ ] Implement the minimal internal helper surface needed to make those tests pass.
- [ ] Ensure the tests cover the v1 safety rules called out in the spec: bounded-height gating for general containers, `width=None, height bounded` support, fail-open on width instability, and `inner_frame.dims`-based budgeting.
- [ ] Add focused helper tests for hierarchical granularity selection: coarse-threshold calculation, skip-level descent, `3 x many` nested structures, and parent-level restart when a deeper path underfills the viewport.
- [ ] Verify that path selection uses cheap metadata only and fails open when safe cheap counts are unavailable.

**Acceptance focus:** The helper can distinguish safe vs unsafe pruning opportunities and returns original content in every inconclusive case.

### Task 2: Wire pruning into `pretty.py` with probe-render flag and per-render memoization

**Purpose:** Connect the tested helper to the real pretty-print path without changing renderer ownership of final output.

**Files:**
- Modify: `src/omnipy/data/_display/text/pretty.py`
- Modify: `src/omnipy/data/_display/text/preview_pruning.py`
- Modify: `tests/data/display/text/test_pretty.py`
- Modify: `tests/data/test_model.py`

- [ ] Add failing integration/contract tests showing that bounded-height previews, including `width=None, height bounded` cases, can avoid preparing heavy invisible tails while preserving the visible viewport.
- [ ] Add the internal probe-render control needed so probe renders observe real formatting for candidate prefixes without recursively re-entering pruning.
- [ ] Add per-render memoization only at the scope needed to reuse repeated probe work within one top-level display call.
- [ ] Implement the selected-path descent and parent-promotion restart behavior without changing prefix-only semantics or introducing sibling holes.
- [ ] Verify the explicit fail-open paths: `height=None`, width instability at the cap, recursion/cycle protection, unavailable cheap metadata, and probe exceptions.

**Acceptance focus:** Real preview code paths honor the helper’s safety rules, and tests prove the visible output contract rather than helper internals alone.

**User Check-in:** Review the integration-test outcomes for the new pruning path before proceeding to the separate `Dataset.list()` optimization.

### Task 3: Add bounded-row optimization to `display._list()`

**Purpose:** Apply the same front-of-viewport work reduction to `Dataset.list()` without changing public behavior.

**Files:**
- Modify: `src/omnipy/data/_mixins/display.py`
- Modify: `tests/data/test_dataset.py`

- [ ] Add failing tests that prove only visible rows plus a small safety margin are materialized for bounded-height `list()` output.
- [ ] Implement the smallest internal helper or local restructuring needed to limit row metadata and string preparation.
- [ ] Verify that row numbering, column content, and visible output stay unchanged, and that the height budget is based on the content viewport already assigned by the layout/panel system.

**Acceptance focus:** `Dataset.list()` does less hidden-row work while preserving current visible output.

### Task 4: Run focused tests, then broader verification

**Purpose:** Confirm the completed slice matches both the revised spec and the regression suite.

**Files:**
- No new production files expected

- [ ] Run the focused unit and integration commands for the touched display/pruning paths.
- [ ] Run broader repository verification appropriate for the scope.
- [ ] Run `pre-commit` in manual/all-files mode and fix only issues caused by this slice.
- [ ] Compare the final behavior against the revised spec and call out any intentional divergence before handoff.

**Acceptance focus:** Fresh verification evidence exists for the helper tests, display contracts, and repo gates before the work is presented as complete.

**User Check-in:** Present test evidence and any remaining risks before asking for final approval on the implementation slice.

## Handoff notes for implementers

- Prefer contract/integration tests over narrow unit tests when validating renderer-visible behavior.
- Use real/instrumented checks instead of mocks where the spec calls for proving reduced preparation/materialization work.
- Keep changes surgical: this plan does not authorize widening scope into new content-type support, public API design, or generalized layout refactors.
- Focus the first nested-granularity regression slice on representative `3 x many` structures before considering any broader heuristic tuning.
