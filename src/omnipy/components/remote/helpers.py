"""Async HTTP helpers for rate limiting and retry strategy selection."""

import asyncio
from collections import deque
from collections.abc import Coroutine, Generator
import math
from types import TracebackType
from typing import Any, NamedTuple

from omnipy.shared.enums.data import BackoffStrategy
from omnipy.shared.typing import TYPE_CHECKING

from .lazy_import import (
    ClientSession,
    ExponentialRetry,
    FibonacciRetry,
    JitterRetry,
    RandomRetry,
)

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from aiohttp.typedefs import StrOrURL

DEFAULT_BURST_RATIO = 0.5

# Tolerance for comparing times that are computed by floating-point arithmetic. For instance, a
# start that is planned for the moment an earlier start leaves the time period may come out a
# fraction of a nanosecond early. Times this close are treated as equal. The tolerance is absolute,
# which suits times in seconds from the monotonic clock of the event loop: a tolerance relative to
# the clock value would grow with the uptime of the system
FLOAT_TOLERANCE = 1e-9


class StartPlan(NamedTuple):
    """A start planned by ``RequestPacer.plan_start()``, to be passed to ``record_start()``."""

    start: float
    # The previous start the plan is based on
    prev_start: float | None
    # The spacing for the following requests, and the time the start that set it leaves the time
    # period. No spacing means that it is calculated anew for the next request
    spacing: float | None
    spacing_valid_until: float


class RequestPacer:
    """
    Decides when rate-limited requests may start, for requests handled one at a time in order.

    Guarantees, for ``requests_per_time_period`` (R) requests per ``time_period_in_secs`` (P) and a
    burst size B:

    - at most R requests start within any time period, wherever the period is placed;
    - at most B + (R/P)·t requests start within any interval of length t (a leaky-bucket bound);
    - while requests are waiting, they keep being started: the pace may slow down after a burst,
      but there are no pauses.

    While fewer than B requests have started within the last time period, a request starts as soon
    as it is ready (a burst). Otherwise, the requests are spaced out. The spacing is the largest of
    ``(leaves - previous_start) / (free + m)`` over the starts within the last time period, where
    ``leaves`` is the time the m-th of these starts leaves the time period and ``free`` is the
    number of further starts the time period allows. This is the fastest even pace from the
    previous start that never needs to wait for a start to leave the time period.

    The spacing stays the same until the start that set it has left the time period, a request
    starts later than the spacing allows (it was not ready), or a burst happens. It is only
    calculated anew at these points. Among starts giving the same spacing, the one that leaves
    the time period last sets it, so that it holds as long as possible.

    The class has no clock: callers pass the times. A start is planned with ``plan_start()``,
    which changes nothing, and the plan is passed to ``record_start()`` when the request starts.
    A request that is cancelled before it starts thus leaves no trace. See
    docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-design.md for the design.
    """

    def __init__(
        self,
        requests_per_time_period: int,
        time_period_in_secs: float,
        burst_ratio: float = DEFAULT_BURST_RATIO,
    ) -> None:
        if (
            isinstance(requests_per_time_period, bool)
            or not isinstance(requests_per_time_period, int)
            or requests_per_time_period < 1
        ):
            raise ValueError(
                f'requests_per_time_period must be a positive integer, '
                f'not {requests_per_time_period!r}'
            )
        if not time_period_in_secs > 0:
            raise ValueError(f'time_period_in_secs must be positive, not {time_period_in_secs!r}')
        if not 0 < burst_ratio < 1:
            raise ValueError(f'burst_ratio must be between 0 and 1, not {burst_ratio!r}')

        self._requests_per_time_period = requests_per_time_period
        self._time_period_in_secs = time_period_in_secs
        self._burst_size = max(
            1, math.floor(burst_ratio * requests_per_time_period + FLOAT_TOLERANCE)
        )

        # Starts within the last time period, in order. The latest start is always kept, as the
        # reference for the next one
        self._starts: deque[float] = deque()

        # The current spacing, and the time the start that set it leaves the time period
        self._spacing: float | None = None
        self._spacing_valid_until = 0.0

    @property
    def requests_per_time_period(self) -> int:
        return self._requests_per_time_period

    @property
    def time_period_in_secs(self) -> float:
        return self._time_period_in_secs

    @property
    def burst_size(self) -> int:
        return self._burst_size

    @property
    def requests_per_second(self) -> float:
        """Return the configured steady-state request rate."""
        return self._requests_per_time_period / self._time_period_in_secs

    def plan_start(self, ready_time: float) -> StartPlan:
        """Plan the start of the next request, which is ready at ``ready_time``.

        The pacer is not changed, so a request that is cancelled before it starts does not affect
        the following ones. Pass the plan to ``record_start()`` when the request starts.
        """
        prev = self._last_start
        now = ready_time if prev is None else max(ready_time, prev)

        if prev is None or self._num_starts_in_time_period(now) < self._burst_size:
            return StartPlan(start=now, prev_start=prev, spacing=None, spacing_valid_until=0.0)

        spacing, spacing_valid_until = self._spacing, self._spacing_valid_until
        if (
            spacing is None
            or prev >= spacing_valid_until - FLOAT_TOLERANCE
            or now > prev + spacing + FLOAT_TOLERANCE
        ):
            spacing, spacing_valid_until = self._calculate_spacing(now, prev)

        if now > prev + spacing + FLOAT_TOLERANCE:
            # The request was not ready in time, so its start is the new reference point
            return StartPlan(start=now, prev_start=prev, spacing=None, spacing_valid_until=0.0)

        return StartPlan(
            start=max(now, prev + spacing),
            prev_start=prev,
            spacing=spacing,
            spacing_valid_until=spacing_valid_until,
        )

    def record_start(self, plan: StartPlan, start_time: float) -> None:
        """Record that the request planned by ``plan`` has started at ``start_time``.

        The start may be a little later than planned, e.g. when the event loop is busy. The
        planned spacing is then kept, which only paces the following requests a little slower
        than needed.
        """
        if plan.prev_start != self._last_start:
            raise ValueError('The plan is not based on the latest start. Plan the start again')
        if start_time < plan.start - FLOAT_TOLERANCE:
            raise ValueError(f'The request started at {start_time}, before its plan ({plan.start})')

        self._spacing = plan.spacing
        self._spacing_valid_until = plan.spacing_valid_until
        self._starts.append(start_time)
        while len(self._starts) > 1 and not self._is_in_time_period(self._starts[0], start_time):
            self._starts.popleft()

    @property
    def _last_start(self) -> float | None:
        return self._starts[-1] if self._starts else None

    def _is_in_time_period(self, start: float, now: float) -> bool:
        return start > now - self._time_period_in_secs + FLOAT_TOLERANCE

    def _num_starts_in_time_period(self, now: float) -> int:
        num_left = 0
        for start in self._starts:
            if self._is_in_time_period(start, now):
                break
            num_left += 1
        return len(self._starts) - num_left

    def _calculate_spacing(self, now: float, prev: float) -> tuple[float, float]:
        in_time_period = [start for start in self._starts if self._is_in_time_period(start, now)]
        num_free = self._requests_per_time_period - len(in_time_period)

        spacing = -math.inf
        valid_until = prev
        for m, start in enumerate(in_time_period, start=1):
            leaves = start + self._time_period_in_secs
            candidate = (leaves - prev) / (num_free + m)
            # Among equal candidates, the start that leaves last sets the spacing
            if candidate >= spacing - FLOAT_TOLERANCE:
                spacing = max(spacing, candidate)
                valid_until = leaves
        return spacing, valid_until


class RateLimiter:
    """
    Lets rate-limited requests wait for their turn, in the order they arrive.

    The timing follows RequestPacer, using the monotonic clock of the event loop. A wait that is
    cancelled does not count as a start.
    """

    def __init__(
        self,
        requests_per_time_period: int,
        time_period_in_secs: float,
        burst_ratio: float = DEFAULT_BURST_RATIO,
    ) -> None:
        self._pacer = RequestPacer(requests_per_time_period, time_period_in_secs, burst_ratio)
        self._lock = asyncio.Lock()

    @property
    def pacer(self) -> RequestPacer:
        return self._pacer

    async def wait(self) -> None:
        """Wait until the next request may start."""
        async with self._lock:
            loop = asyncio.get_running_loop()
            plan = self._pacer.plan_start(loop.time())
            delay = plan.start - loop.time()
            if delay > 0:
                await asyncio.sleep(delay)
            self._pacer.record_start(plan, max(plan.start, loop.time()))


class _RateLimitedRequest:
    """A request that can be awaited, or used with ``async with``, like those of aiohttp."""

    def __init__(self, response_coro: Coroutine[Any, Any, 'ClientResponse']) -> None:
        self._response_coro = response_coro
        self._response: ClientResponse | None = None

    def __await__(self) -> Generator[Any, None, 'ClientResponse']:
        return self._response_coro.__await__()

    async def __aenter__(self) -> 'ClientResponse':
        self._response = await self._response_coro
        return self._response

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self._response is not None
        self._response.release()
        await self._response.wait_for_close()


class RateLimitingClientSession:
    """
    An HTTP client session that limits the requests to ``requests_per_time_period`` per
    ``time_period_in_secs``, allowing an initial burst of requests.

    The session wraps an aiohttp ClientSession, which gets all other arguments. Each request waits
    for its turn (see RateLimiter and RequestPacer) before aiohttp starts it, so that the timeouts
    of aiohttp count from the actual start of each request. The session offers what
    aiohttp_retry.RetryClient uses (``request()`` and ``close()``), so that each retry attempt is
    rate limited as well, plus ``get()`` and ``post()``.
    """

    def __init__(
        self,
        requests_per_time_period: int,
        time_period_in_secs: float,
        *args: Any,
        burst_ratio: float = DEFAULT_BURST_RATIO,
        **kwargs: Any,
    ) -> None:
        self._limiter = RateLimiter(requests_per_time_period, time_period_in_secs, burst_ratio)
        self._session = ClientSession(*args, **kwargs)

    @property
    def requests_per_time_period(self) -> int:
        return self._limiter.pacer.requests_per_time_period

    @property
    def time_period_in_secs(self) -> float:
        return self._limiter.pacer.time_period_in_secs

    @property
    def burst_size(self) -> int:
        return self._limiter.pacer.burst_size

    @property
    def requests_per_second(self) -> float:
        """Return the configured steady-state request rate."""
        return self._limiter.pacer.requests_per_second

    @property
    def closed(self) -> bool:
        return self._session.closed

    def request(self, method: str, url: 'StrOrURL', **kwargs: Any) -> _RateLimitedRequest:
        return _RateLimitedRequest(self._request(method, url, **kwargs))

    def get(self, url: 'StrOrURL', **kwargs: Any) -> _RateLimitedRequest:
        return self.request('GET', url, **kwargs)

    def post(self, url: 'StrOrURL', **kwargs: Any) -> _RateLimitedRequest:
        return self.request('POST', url, **kwargs)

    async def _request(self, method: str, url: 'StrOrURL', **kwargs: Any) -> 'ClientResponse':
        await self._limiter.wait()
        return await self._session.request(method, url, **kwargs)

    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> 'RateLimitingClientSession':
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()


BACKOFF_STRATEGY_2_RETRY_CLS = {
    BackoffStrategy.EXPONENTIAL: ExponentialRetry,
    BackoffStrategy.JITTER: JitterRetry,
    BackoffStrategy.FIBONACCI: FibonacciRetry,
    BackoffStrategy.RANDOM: RandomRetry,
}
