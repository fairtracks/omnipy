# Rate limiter pacing: design

Status: implemented (2026-10-24)

Implementation plan: `docs/agents/technical/plans/2026-10-24-rate-limiter-pacing-implementation.md`

## Background

`RateLimitingClientSession` (`src/omnipy/components/remote/helpers.py`) limits the requests to one
host to `requests_per_time_period` (R) per `time_period_in_secs` (P), configured per host in
`HttpRequestsConfig`. The original design combined an `aiolimiter.AsyncLimiter` (a leaky-bucket
meter with its capacity lowered to a burst of R/2 + 1 and a leak rate of R/P) with a home-made
compensation delay after the burst, so that the burst would not push the total above R per P.

The compensation was only correct when all requests arrived at once. Its state (a cumulative
delay, a request counter and a reset when a request arrived more than P after the first one) broke
down for requests arriving over time, after event-loop stalls, and between batches: up to 15
requests were started in one period of 10, and 21 requests took 0.76 s instead of 1.0 s. A
test-bounds widening (`fc105141`) hid this, and three later attempts (`5a731635`, `dfe37c55`,
`61ee1849`) solved other requirements than the intended ones. This design replaces all of it.

Two further findings shape the design:

- The limiter waits in aiohttp's `on_request_start` trace hook. aiohttp starts the total-timeout
  clock before that hook. A request that waits longer than its total timeout in the limiter then
  runs without any timeout (verified on aiohttp 3.14.5: with 1 request per 2 s and a total timeout
  of 1.5 s, requests that waited 2 s and 4 s ran 5 s against a slow server without timing out).
- `aiohttp_retry`'s `RetryClient` calls the session's `request()` once per attempt, and sleeps for
  the backoff outside the session. Every attempt therefore passes through the limiter.

## Requirements

For each session, with R requests per P seconds and a burst size B:

1. **Leaky-bucket bound**: at most B + (R/P)·t requests start within any interval of length t.
2. **Window bound**: at most R requests start within any window of length P, wherever it is
   placed. This makes the client safe for servers that count with fixed or sliding windows.
3. **No gaps, only frequency shifts**: while requests wait, they keep being started; the pace may
   slow down after a burst but never stops. Users waiting for responses should not think that
   something is wrong.
4. **Quick response**: small requests (up to B at once, when the window is not already busy) start
   immediately.
5. **Nothing is dropped**: requests wait in line, in the order they became ready.

## Concepts

The design is explained with a contraption (the interactive simulation in the docs shows it):

- Waiting requests are balls in a **bucket**. A **valve** at its bottom lets them out one at a
  time into a **pipe** that takes P seconds to pass through. The pipe clogs if it holds more than R
  balls (requirement 2).
- A **camera** watches the pipe: the start times of the requests started within the last P
  seconds, and so the time each one leaves the window.
- A **controller** sets the valve from what the camera sees.

## The pacing rule

Requests are handled one at a time, in the order they became ready. For the request that is first
in line at time `now` (never earlier than the previous release `prev`):

1. Remove from the pipe the starts that are P or more seconds old.
2. **Burst**: if fewer than B balls are in the pipe, start the request now. A burst is thus every
   start made while fewer than B balls are in the pipe, whether the requests arrived together or
   one after another.
3. **Paced**: otherwise, let `free = R - (balls in the pipe)` and `e_1 <= e_2 <= ...` the times at
   which the balls in the pipe leave it (start time + P). The valve setting is the spacing

       g = max over m of (e_m - prev) / (free + m)

   and the request starts at `max(now, prev + g)`. The setting is always measured from the
   previous start `prev`, whether that start was part of a burst or paced.

When several balls give the same largest spacing (a tie, e.g. in a steady backlog where all of
them do), the ball that leaves the pipe **last** counts as the one that sets the valve. That keeps
the setting valid for as long as possible (see the segments below).

### Why this works

- For ball m, `(e_m - prev) / (free + m)` is the spacing at which evenly spaced starts from `prev`
  fill the pipe exactly when ball m leaves it: `free + m - 1` more starts fit before then, plus one
  at that moment. Taking the largest of these spacings gives the fastest pace that never runs into
  a full pipe, so requirement 2 holds without any waiting for the window (requirement 3).
- The newest ball always gives `P / R`, so g is never below the steady interval, and the rule
  never starts requests faster than R/P after a burst. Together with the burst size B this gives
  requirement 1: in simulations the bucket bound was never exceeded, and an `AsyncLimiter` with
  capacity B and rate R/P in front of the rule changed no start time in 3,000 random runs.
- Considering only the balls released as bursts is not enough: a ball released on a narrowed
  valve and followed closely by a small burst can be the one that limits. In 13,500 random runs,
  the burst-only variant exceeded R per window in 365 runs.

### Behaviour: the valve setting changes in segments

The setting stays constant in segments. A segment begins at the start the setting is measured
from (the previous start when the setting is computed), and lasts until the first of:

1. the ball that set it leaves the pipe (the segment's last start coincides with that moment);
2. a request is ready only later than `prev + g` (the bucket ran empty): it starts at once, and
   the next setting is measured from its start;
3. a burst (fewer than B balls in the pipe).

When a request is first in line and no setting is in force, the controller computes one from the
previous start. If the request is ready later than the earliest start this allows, the
calculation has only served as a check that the request may start now: it starts at once, and the
next setting is measured from its start (case 2). Example (R = 10, P = 0.5 s, B = 6): after a
burst of 6 ending at 0.300 s, request 7 arrives at 0.400 s; the check gives an earliest start of
0.383 s, so request 7 starts at 0.400 s, and the next setting, 1 per 0.080 s, is measured from
there.

The implementation computes the setting only at these boundaries, and otherwise starts each
request at `max(now, prev + g)` with the current setting. This gives exactly the same start times
as computing the setting for every request (verified in 18,000 random runs with R of 4, 10 and 20
and burst ratios of 0.3, 0.5 and 0.7).

The tie rule is what makes this pay off. In a steady backlog all balls tie, and with the earliest
one as the limiting ball every segment would end after one start. With the latest one, a segment
lasts a whole period. Measured numbers of computations of the setting, per ball (every request
that is not part of a burst) and per segment (with the tie rule):

| Workload | R = 10 per 0.5 s: per ball | per segment | R = 60 per 60 s: per ball | per segment |
|---|---|---|---|---|
| one batch of 1,000 requests | 995 | 100 | 970 | 17 |
| three batches of 300, with pauses | 885 | 90 | 810 | 15 |
| a batch of 500 plus 50 retries | 545 | 55 | 520 | 10 |
| random arrivals (900,000 starts, R of 4, 10 and 20) | 71 % of the starts | 19 % | - | - |

With the earliest tied ball as the limiting one instead, the segment form would compute the
setting nearly as often as the per-ball form (e.g. 981 times for the batch of 1,000 at R = 10).

So for batches, which are the main use (`Dataset.load()`), the full calculation (O(R)) runs about
once per R requests. Per request, only the count of balls in the pipe is needed, which a deque of
start times gives in O(1) amortized time. The per-request form remains in the tests as the
reference that the segment form must match.

While requests wait, the spacing never exceeds `P / (R - B + 1)`, the ramp right after a full burst
(verified for R from 2 to 60 and burst ratios 0.3 to 0.9). Example for R = 10, P = 0.5 s, B = 5 and
21 requests at once: 5 start at once, the next 5 about 0.083 s apart, then 20/s from 0.5 s.

## Burst size

`B = max(1, floor(burst_ratio * R))`. The `+ 1` of the original design is dropped (it only made
the ramp round for R = 10).

- `burst_ratio` is configurable per host in `HttpRequestsConfig`, default 0.5, and must satisfy
  `0 < burst_ratio < 1`. With a ratio of 1 a burst fills the pipe and the next request must wait a
  full period, which is a gap.
- With the default host configuration (60 requests per 60 s) the burst is 30 requests, after
  which requests start about 1.94 s apart until the burst has left the window, then 1 s apart.

## Number of slots

`requests_per_time_period` becomes an `int` (it is a float today), with a minimum of 1. The pipe
holds R balls and the steady interval is `P / R`. A float value given in a configuration must not
be truncated silently (pydantic v1 coerces floats to int), so the field rejects non-integral
values.

## Waiting before the request starts

The waiting must happen before aiohttp starts the request, so that each attempt's timeout counts
from its own start. Findings for aiohttp 3.14.5 and aiohttp_retry:

- `ClientSession._request` starts the total-timeout clock before it sends the `on_request_start`
  trace (used today) and before it calls client middlewares, so neither hook works.
- Overriding `ClientSession._request` would work, but it is a private method, and aiohttp
  discourages subclassing `ClientSession` (it warns when a subclass is defined).
- `RetryClient` only uses `request()` and `close()` of the session it wraps.

Decision: composition instead of subclassing. The pacing rule lives in a limiter object, and a
small adapter holds a plain `ClientSession`. Its `request()` waits in the limiter and then calls the
session's `request()`; its `close()` closes the session. `RetryClient` wraps the adapter, so every
attempt waits before aiohttp starts it, using public API only. For code that uses the adapter
without `RetryClient`, it also offers `get()` and `post()` built on its `request()`.

A test pins the behaviour: a request delayed by the limiter must still time out.

An alternative for later is to replace `aiohttp_retry` with an own retry loop that waits in the
limiter before each attempt. That would fit the follow-up work on `Retry-After` and the circuit
breaker (out of scope below), but is more than this change needs.

## Retries

Each retry attempt passes through the limiter like any other request (it is a request to the host,
and the host counts it). After its backoff, a retry joins the line at the back, in the order it
became ready again. Putting retries first would let requests that tend to fail again take the next
starts repeatedly, ahead of fresh requests.

## Clock, ordering and cancellation

- Times come from the event loop's monotonic clock (`loop.time()`), not `datetime.now()`.
- An `asyncio.Lock` (FIFO) serializes the decisions, so each request sees the previous start.
- A request cancelled while it waits does not start and leaves no ball in the pipe.

## Removed

- `AsyncLimiter` from the rate limiter. `aiolimiter` is used nowhere else, so the dependency in
  `pyproject.toml` and the import in `src/omnipy/components/remote/lazy_import.py` are removed.

## Out of scope (TODOs in `Dataset._load_http_urls`)

- Sharing the rate limiting per host across Dataset loads (today one session per host per load).
- Detecting that a host is down or overloaded (circuit breaker), including `Retry-After` handling
  of 429 responses.

## Documentation

A Learn page (`docs/learn/rate-limiting.md`) explains the requirements, the contraption and the
pacing rule, and embeds the interactive simulation (a standalone HTML file under `docs/learn/`) in
an iframe. The configuration reference and Tutorial 6 link to it.

The interactive simulation used for this design is kept as a working copy in
`docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-simulation.html` (it opens directly
in a browser). The published version in `docs/learn/` is derived from it. The simulation is a JavaScript
model of the rule; a test runs the Python implementation on the simulation's scenarios and checks
the same start times, so the two cannot drift apart unnoticed.

## Decisions

1. `burst_ratio` is a per-host field of `HttpRequestsConfig` (default 0.5).
2. `requests_per_time_period` becomes an `int` (minimum 1).
3. The four superseded limiter commits are dropped from the unpushed history.
4. The waiting happens in a session adapter (composition), not in a `ClientSession` subclass.
