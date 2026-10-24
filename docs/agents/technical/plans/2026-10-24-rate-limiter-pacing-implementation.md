# Rate limiter pacing: implementation plan

Status: draft for approval (2026-10-24, revised the same day)

Design: `docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-design.md`

Each step ends with its own commit. Verification commands follow `AGENTS.md`; tests run with
`env -u OMNIPY_NO_PREFECT_TEST_HARNESS uv run pytest ...` in this environment.

## 1. Start from the original limiter

Drop the four superseded limiter commits from the (unpushed) `ruff` branch with an interactive
rebase: `fc105141` (widened run-time bounds), `5a731635`, `dfe37c55` and `61ee1849`. Check that
`src/omnipy/components/remote/helpers.py` and `tests/components/remote/test_helpers.py` then match
the base commit `a62c57e5` apart from the ruff migration.

## 2. Pacing rule without asyncio

In `src/omnipy/components/remote/helpers.py`, add the pacing rule as plain code without asyncio or
a clock: a small class holding the start times in the pipe (a deque), the previous start and the
current valve setting (spacing and the time it is valid until), with a method that takes the time
the next request is ready and returns its start time. It computes the setting only at segment
boundaries (the setting's ball has left, a late start, a burst), with the tie rule of the design.
This can be tested exhaustively and fast.

In the tests, a reference implementation that recomputes the setting for every request, and a
property test that both give the same start times.

Tests (new, in `tests/components/remote/test_helpers.py` or a sibling module), with a seeded
pseudo-random generator (no new dependency), many arrival patterns, R in {1, 2, 4, 10, 20, 60} and
burst ratios in {0.3, 0.5, 0.7, 0.9}, asserting for the computed start times:

- at most R starts in any window of length P;
- at most B + (R/P)·t starts in any interval of length t;
- while a request waits, the spacing between starts never exceeds `P / (R - B + 1)`;
- a burst of up to B requests at once starts immediately when the window is empty;
- starts are in the order the requests became ready.

Plus fixed scenarios with exact expected start times: the six scenarios of the simulation page.

## 3. Limiter and session adapter

Replace `RateLimitingClientSession` (the `AsyncLimiter`, the compensation and the trace hook) with:

- a limiter: an `asyncio.Lock`, the pacing rule from step 2, and a `wait()` method that takes the
  lock, gets the start time for `loop.time()`, sleeps until then and records the start; a request
  cancelled while it waits records nothing;
- a session adapter (composition, no subclass of `ClientSession`) holding a plain `ClientSession`:
  `request()` waits in the limiter and then calls the session's `request()`, `close()` closes the
  session, plus `get()`/`post()` built on `request()`, and `async with` support;
- `B = max(1, floor(burst_ratio * R))`, rejecting `burst_ratio` outside (0, 1) and R below 1.

Keep the names and parameters the callers use where possible (`RateLimitingClientSession`,
`requests_per_second`), adding `burst_ratio: float = 0.5`. Adapt `get_retry_client()`,
`_ensure_retry_session()` and `Dataset._load_http_urls` to the adapter.

Tests: restore the run-time bounds of `test_rate_limiting_client_session` to a lower bound of
1.0 s (upper bound 1.2 s), and add a session-level test that records the start times of real
requests against the test server (all at once and spread out) and checks the window bound and the
no-gap bound with a small tolerance for scheduler noise.

## 4. Timeouts count from the start of each attempt

With the adapter, the waiting happens before aiohttp starts a request. Test: a session with 1
request per 2 s and a total timeout of 1.5 s against a server that answers after 5 s; every
request, including those that waited in the limiter, must time out about 1.5 s after it was
started. Also through `RetryClient`, with retries.

## 5. Configuration

In `HttpRequestsConfig` (`src/omnipy/config/data.py`) and `IsHttpRequestsConfig`
(`src/omnipy/shared/protocols/config.py`):

- `requests_per_time_period` becomes an `int` with a minimum of 1, rejecting non-integral values
  instead of truncating them;
- add `burst_ratio: float = 0.5`, validated to lie strictly between 0 and 1.

Pass `burst_ratio` in `Dataset._load_http_urls` (`src/omnipy/data/dataset.py`). Update the config
tests and the configuration reference.

## 6. Remove `aiolimiter`

Remove the dependency from `pyproject.toml` and the import from
`src/omnipy/components/remote/lazy_import.py`, after checking that nothing else uses it.

## 7. Documentation

- `docs/learn/rate-limiting.md`: requirements, the contraption, the pacing rule, segments, burst
  ratio, retries; embed the simulation in an iframe with a link to open it on its own. Add it to
  the `Learn` section of `mkdocs.yml`.
- The simulation as a standalone HTML file under `docs/learn/` (a full HTML document, the docs'
  light colour scheme, no external fonts), with the burst ratio selector and the six scenarios.
- Links from `docs/reference/configuration.md` (per-host HTTP settings) and
  `docs/tutorials/06-resilient-api.md`.
- A test that runs the pure function on the simulation's scenarios and compares the start times
  with those the page computes (scenario data and expected values kept in one place that both use,
  or checked in the test against the page's JavaScript output recorded once).
- Release notes entry.

## 8. Verification

- Full test suite (`env -u OMNIPY_NO_PREFECT_TEST_HARNESS uv run pytest tests`), and the remote
  tests repeated under CPU load.
- `uv run prek run --all-files`.
- `uv run mkdocs build` (not yet verified on this branch), and a look at the embedded simulation.
- mypy and basedpyright diagnostics not above the current counts.
