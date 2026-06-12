Title: Per-panel pruning before pretty-printers — renderer-guided rendered-prefix superset (adopted C)

Overview
- Purpose: reduce the amount of model/dataset content prepared and sent to pretty-printers for `peek()`/`full()`/`json()`/`list()` displays by returning a slightly-more-than-visible front prefix for each panel. The pruner does not add ellipses or otherwise change final rendering; it only supplies less input. Rendering, cropping, and ellipsis behavior remain the responsibility of existing pretty-print and display layers.
- Key design decision (adopted): use a renderer-guided rendered-prefix superset strategy (C). For a safely gated bounded panel, probe incremental prefixes under the actual panel frame and stop once a bounded heuristic probe window suggests the prefix is sufficient for the visible viewport. Cap probes to avoid worst-case full scans, and fail open whenever safety cannot be established.

Goals & constraints
- Goals
  - Avoid preparing or converting large tails of model or dataset data when those tails cannot affect the visible preview for that panel.
  - Prune from the front only by returning the minimal slightly-more-than-visible whole-item prefix needed to preserve the visible viewport.
- Preserve current rendering architecture and public methods.
- Keep the optimization best-effort and safe by fail-open; do not claim exactness beyond the current heuristic stopping rules.
- Constraints
- Only ordered or sequence-like and insertion-ordered mapping types are guaranteed to be prunable in v1.
- For general container pretty-printing in v1, pruning is only enabled when height is bounded. Width may be bounded or unbounded; `width=None, height bounded` previews may prune, while `height=None` previews skip pruning regardless of width.
- For unbounded-height `full()` calls, pruning is skipped; do not change semantics.
- The pruner must fail open: any error or unsupported case falls back to current behavior.
- The pruner must not insert ellipses.
- Strings and bytes are treated as sequences in pruner logic.

Architecture & components
- Primary hook location (recommended)
  - `src/omnipy/data/_display/text/pretty.py`
  - Add an internal pre-format pruning step invoked immediately before expensive prepare or format operations for a `DraftPanel`.
  - This hook receives the `DraftPanel` (`content`, `frame`, `config`) and returns either the original or a pruned `DraftPanel` instance.
- New helper module (internal)
  - `src/omnipy/data/_display/text/preview_pruning.py`
  - Implement the pruner and probe orchestration. Expose only private functions used by `pretty.py`.
  - Responsibilities: budget derivation, prefix probe orchestration, per-top-level-render-call caching, recursion and cycle guards, and fail-open safety fallbacks.
- Minor display-layer changes
  - `src/omnipy/data/_mixins/display.py`
  - Keep top-level panel count limiting as-is.
  - Add a bounded-row optimization for `Dataset.list()` so it builds only visible rows plus a small safety margin and avoids preparing metadata for rows outside the visible range.
- Avoid changing
  - `DraftPanel`, `Layout`, `PanelDesignDims`, and `render_next_stage()`.
  - Prefer using the panel frame already assigned by layout before `pretty.py` is called.
- Optional internal-only utility
  - Add a small internal probe-render flag that allows the pruner to render candidate prefixes for probing without recursively re-entering pruning. Probe renders must observe the real rendering behavior of the unpruned candidate prefix.

Data flow & algorithms
- When pruning runs
  - Pruning runs for a `DraftPanel` when:
    - content is sequence-like or mapping-like and ordered enough to slice safely;
    - the panel viewport has bounded height for the content shape being rendered; width may be bounded or unbounded, with width stabilization used only when width is known;
    - the pruner recognizes the content shape as safe to slice into whole logical items or chunks.
  - Pruning is skipped and the original `DraftPanel` is forwarded if:
    - the content type is unsupported, such as unordered sets or opaque objects;
    - `height_budget` is `None`, including `full()` and other effectively unbounded-height paths, regardless of width;
    - a probe or render error occurs;
    - recursion or cycles cannot be handled safely;
    - both width and height are effectively unbounded.
- `PanelPreviewBudget` derivation
  - Derive viewport budgets from `draft_panel.inner_frame.dims` and `draft_panel.config`, i.e. from the title-adjusted content area already assigned by layout and panel machinery:
    - `width_budget`: panel content width in characters, if available;
    - `height_budget`: panel content height in lines, if available; if `None`, treat height as unbounded and do not apply a vertical cutoff;
    - do not subtract title height or panel chrome again here; the layout engine has already accounted for that before the panel reaches the pruner;
    - formatting inputs needed for faithful probe renders, including indentation, tab size, and pretty-printer choice.
- Hierarchical chunking-path selection (single active path)
  - Goal: choose a pruning level with useful chunk granularity before probe rendering, while preserving strict prefix-only, no-holes semantics.
  - The pruner uses one active chunking path at a time. It starts at the root path and may descend into the first eligible child path in existing container order when the current level is too coarse.
  - Coarse-ness threshold:
    - `H = height_budget`
    - `w = width_stabilization_window`
    - `T_base = max(2 * H, H + w + 1)` when `H` is known, otherwise `16`
    - `T_eff = max(4, ceil(alpha * T_base))`
    - A level is considered too coarse when `chunk_count(level) < T_eff`.
  - Path-selection steps:
    1. Start at the root path `/`.
    2. Compute a cheap `chunk_count` for the current path.
    3. If `chunk_count >= T_eff`, select the current path.
    4. Otherwise descend to the first eligible child path in existing container order and repeat, allowing multiple coarse intermediate levels to be skipped until a suitable path is found, `max_descent_depth` is reached, or no eligible child remains.
    5. If no suitable path is found, select the deepest visited path along that deterministic descent chain.
    6. Run probe search only on that selected path.
    7. If the selected deeper path is fully consumed and the viewport is still underfilled, promote to the parent path and restart there from prefix start.
    8. Stop after `max_promotions`; if the viewport still cannot be filled safely, fail open.
  - Coarse-ness evaluation must use cheap metadata only and must not trigger expensive chunk construction or full materialization. In particular, it must avoid full `splitlines()` over large text, full `list(mapping.items())`, deep traversal, or model/data conversion done solely to choose a path.
  - If cheap count metadata is unavailable or unsafe for a node, do not descend through that node; keep the current already-visited path. If deterministic child order cannot be established safely, fail open instead of choosing among siblings heuristically.
- Probe orchestration (renderer-guided rendered-prefix superset with bounded probes)
  - Goal: return a best-effort front prefix such that, in safely gated cases, rendering that prefix under the same frame, config, and pretty-printer appears sufficient to fill the visible viewport, while keeping probes bounded. If the heuristic cannot establish this safely, return the original input.
  - Steps:
    1. Quick checks: if `height_budget` is `None`, if the user requested effectively unbounded `full()` semantics, or if the content/path cannot be handled safely, skip pruning.
    2. Select the active chunking path using the hierarchical path-selection rules above.
    3. Start with a small prefix (`n = 1` or the smallest logical chunk on the selected path).
    4. Use progressive probing with exponential growth: `n := 1, 2, 4, 8, ...` until one of the following happens:
       - `rendered_height(prefix_n) >= height_budget`;
       - rendered width has stabilized over the configured forward window, when width is bounded and width stabilization is available;
       - `n >= max_probe_items` cap;
       - the end of the selected path is reached.
    5. Each `rendered_*` observation is obtained by a probe render of the candidate prefix using the same pretty-printer and frame, but with pruning disabled for the probe so the probe observes faithful rendering for that candidate prefix.
    6. If probing stopped because height was reached or width stabilized, binary search downward between the previous lower bound and current `n` to find the minimal `n` that still satisfies the heuristic stopping condition.
    7. Keep the existing binary-search behavior in this slice; do not add a new public or plan-visible cap parameter just for binary search refinement.
    8. Return that minimal whole-item or whole-chunk prefix. Do not add ellipses in the pruner.
- Width-window behavior
  - Because `peek()` currently uses rendering to determine effective panel width, the pruner should not keep scanning distant items solely to discover a far-away outlier line that would widen the panel.
  - Width stabilization is heuristic: when width is bounded, width is considered stable when the rendered width no longer changes across a small forward window of probe extensions, or when extending by a small delta does not change rendered width.
  - Recommended internal default: a width stabilization window of 2 to 3 forward checks.
  - If width does not stabilize before the probe cap, fail open and return the full unpruned content.
- Implemented width-unbounded policy
  - For general container types whose pretty-printers can globally reformat earlier output based on later items — including Rich, Devtools, and CompactJSON rendering over sequences, mappings, and model-shaped containers — the v1 pruning contract remains best-effort and fail-open rather than exact.
  - The implemented v1 policy allows pruning when `width=None` and `height` is bounded, using the same bounded probe strategy and the same fail-open fallback if the viewport cannot be established safely.
  - Pruning is skipped when `height=None`, including full-view paths, regardless of width.
  - Known prefix-stable content shapes, such as line-appending text or fixed-column output, could support stricter width-unbounded reasoning or future allowlists, but that is out of scope for this slice.
- Caps, caching, and fallbacks
  - `max_probe_items` is a private internal cap to prevent worst-case scans; an initial design target is on the order of `1024` logical items or chunks.
  - An optional `max_probe_time` internal cap may be added if needed to bound slow probe loops.
  - `alpha`, `max_descent_depth`, and `max_promotions` are private internal tuning constants for hierarchical path selection.
  - Cache probe render results by `(object identity, prefix size, frame, config, printer)` for the lifespan of a single top-level display call.
  - If any probe throws or recursion is detected, abort pruning for that panel and return the original `DraftPanel`.
- Chunking rules for sequences and strings or bytes
  - Sequences use whole-item prefixes.
  - Strings and bytes are treated as sequence-like content.
  - Prefer line-aware chunking first by splitting on newline boundaries.
  - For very long single-line strings, fall back to fixed-size chunks, for example around 256 characters, to avoid degenerate character-by-character probing.
  - For bytes, use fixed-size logical chunks compatible with byte-oriented or hexdump-like rendering.
  - For nested structures, keep one active chunking path at a time and preserve prefix-only semantics all the way back to the root; never introduce holes across sibling chunks.
- Mappings
  - Use insertion order and include the first `n` key-value pairs as whole pairs.
- Nested panels
  - Top-level panel count limiting remains in `_peek_nested_content()`.
  - For each visible child panel, the pruner still runs in `pretty.py` using the child panel's assigned frame.
- `Dataset.list()`
  - Add a bounded-row construction helper to compute metadata and row strings only for visible rows plus a small safety margin.
  - This keeps `list()` aligned with the same front-prefix principle without changing public behavior.

API changes
- None public.
- Internal-only additions:
  - `preview_pruning` module;
  - small private helpers in `display.py`;
  - private probe-only flags or context values needed to disable recursive pruning during probe renders.
- No new public kwargs.
- Internal configuration such as probe caps and width-window size remains private constants.

Error handling & safety
- Fail open: any inability to safely prune, including exceptions, recursion, unsupported containers, or effectively unbounded display conditions, results in the original behavior.
- Track object identities to prevent infinite recursion on cyclic structures.
- Probe renders must run without entering the pruning loop.
- Keep pruning disabled for any path where safe front-prefix pruning cannot be established.

Performance considerations
- Expected wins
  - Avoid full `to_data()`-style preparation for long tails that are guaranteed invisible to the panel viewport.
  - Reduce expensive conversion and formatting for nested visible panels.
  - Limit `Dataset.list()` work to visible rows plus a small safety margin.
- Probe cost
  - Probe renders add overhead, but the search is bounded by exponential growth followed by binary search and capped by probe limits.
  - In normal cases, this should be materially cheaper than preparing the full dataset or model tail.
- Worst case
  - In degenerate cases with many tiny items and visibility near the end, probe work can approach a scan-like cost.
  - Private caps and fail-open fallback limit this.
- Caching
  - Per-top-level-render-call caching reduces repeated probes for nested, repeated, or structurally similar panels.
- Strings and bytes
  - Chunking avoids excessive tiny probe steps and keeps long single-line content tractable.

Testing plan
- Unit tests for pruning algorithm and helpers
  - `tests/data/display/text/test_preview_pruning.py`
    - `test_sequence_rendered_prefix_superset_stops_at_viewport`: narrow frame, long list with a very long line far away; assert visible viewport content is preserved and the pruned prefix is smaller than the full input.
    - `test_string_chunking_and_pruning`: long single-line string; ensure chunking returns a prefix that fills the viewport and stops.
    - `test_mapping_pruning_insertion_order`: large mapping; assert the first `N` pairs are used in insertion order.
    - `test_probe_caps_and_fallback`: extremely large input; assert the pruner respects probe caps, allows `width=None, height bounded`, skips pruning when `height=None`, fails open if needed, and raises no exception.
    - `test_probe_cache_effectiveness`: repeated pruning on the same object within a single display call should reuse probe results.
    - `test_nested_granularity_descends_for_three_by_many_shape`: a `3 x many` nested structure should descend past coarse top-level chunking and select a finer prefix-preserving path.
    - `test_nested_granularity_promotes_to_parent_when_underfilled`: if the chosen deeper path is exhausted and the viewport is still underfilled, the pruner should promote to the parent path and restart from the parent prefix.
- Integration tests for display behavior
  - `tests/data/test_model.py`
    - `test_model_peek_prunes_large_sequence_before_pretty_printing`: assert heavy tails are not prepared beyond the returned prefix using real/instrumented checks.
    - `test_model_json_pruner_respects_width_and_height`: ensure visible preview rows are preserved for both bounded-width and `width=None, height bounded` previews.
    - `test_model_full_unbounded_height_skips_vertical_pruning`: `full()` semantics remain unchanged for `height=None`.
  - `tests/data/test_dataset.py`
    - `test_dataset_peek_top_level_and_child_panels_pruned`: top-level panel count limiting still applies and child panels are pruned individually using their own frames.
    - `test_dataset_peek_nested_three_by_many_uses_finer_granularity`: nested visible panels with few top-level chunks and large inner tails should use finer path selection without creating holes.
    - `test_dataset_list_bounded_rows_only_materialized`: `list()` computes only visible rows plus safety margin and avoids metadata work for hidden rows.
- Example pytest invocations
  - Internal:
    - `uv run pytest tests/data/display/text/test_preview_pruning.py --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
  - Integration:
    - `uv run pytest tests/data/test_model.py tests/data/test_dataset.py --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
  - Full verification:
    - `uv run pytest -v --mypy-only-local-stub --mypy-pyproject-toml-file=pyproject.toml --mypy-same-process`
  - Pre-commit:
    - `uv run pre-commit run --hook-stage manual --all-files`
- Expected assertions
  - In safe bounded-height cases where pruning runs and the probe stopping criteria stabilize, the visible viewport contains the same content as would be produced by rendering the full model and cropping to the viewport.
  - If width does not stabilize before the probe cap, pruning is skipped and rendering falls back to the full unpruned content.
  - Hidden top-level dataset panels are not materialized.
  - `list()` computes metadata only for visible rows plus the chosen safety margin.

Migration & rollout
- Step 0: add characterization tests that capture current `peek()` and `list()` behavior to guard against regressions.
- Step 1: add the dedicated preview-pruning helper module and unit tests.
- Step 2: wire pruning into `pretty.py` with an internal probe-render flag and per-render memoization.
- Step 3: add the bounded-row optimization to `display._list()`.
- Step 4: run focused tests, then broader verification, and fix regressions.
- Step 5: optionally expand supported types and tune private caps during later planning or implementation work.

Decisions
- Pruning strategy adopted: renderer-guided rendered-prefix superset (C). Probes use the actual assigned panel frame.
- Probe strategy adopted: progressive probing with bounded cap (B). Use exponential growth followed by binary search with bounded probe count.
- Pruner behavior: return a slightly-more-than-visible prefix only.
- Correctness posture adopted: best-effort heuristic with fail-open fallback, not exact/provable pruning.
- Safety gating adopted: v1 general-container pruning requires bounded height; `width=None, height bounded` previews may prune, while `height=None` paths skip pruning regardless of width.
- The pruner must not insert ellipses. Existing rendering layers remain responsible for cropping and ellipsis behavior.
- Strings and bytes are treated as sequences, using line-aware chunking first and fixed-size chunks for long single-line content.
- Hierarchical granularity selection adopted: use a single active chunking path, descend past coarse levels when needed, and promote back to the parent path with restart semantics if a deeper path underfills the viewport.

End of document.
