"""Reference implementation and checks for the pacing of rate-limited requests.

See docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-design.md
"""

from collections.abc import Sequence
import random

from omnipy.components.remote.helpers import RequestPacer

# Tolerance for comparing times that are computed by floating-point arithmetic
EPS = 1e-9


def per_ball_start_times(
    arrivals: Sequence[float],
    requests_per_time_period: int,
    time_period_in_secs: float,
    burst_size: int,
) -> list[float]:
    """Start times from the pacing rule, calculated anew for every request.

    This is the straightforward form of the rule in the design, used as the reference for
    RequestPacer, which only calculates the spacing at the boundaries of segments.
    Arrivals must be in the order the requests are handled.
    """
    starts: list[float] = []
    for arrival in arrivals:
        prev = starts[-1] if starts else None
        ready = arrival if prev is None else max(arrival, prev)
        in_period = sorted(start for start in starts if start > ready - time_period_in_secs + EPS)
        if prev is None or len(in_period) < burst_size:
            starts.append(ready)
            continue
        free = requests_per_time_period - len(in_period)
        spacing = max(
            (start + time_period_in_secs - prev) / (free + m)
            for m, start in enumerate(in_period, start=1)
        )
        starts.append(max(ready, prev + spacing))
    return starts


def pacer_start_times(
    pacer: RequestPacer,
    arrivals: Sequence[float],
    delays: Sequence[float] | None = None,
) -> list[float]:
    """Start times from a RequestPacer, handling the requests one at a time in order.

    With ``delays``, each request starts that much later than planned, as when the event loop
    is busy.
    """
    starts = []
    for i, arrival in enumerate(arrivals):
        start = pacer.plan_start(arrival) + (delays[i] if delays else 0.0)
        pacer.record_start(start)
        starts.append(start)
    return starts


def random_arrivals(rng: random.Random, num: int, time_period_in_secs: float) -> list[float]:
    """Arrival times mixing requests that arrive together, in quick succession and after gaps."""
    time = 0.0
    arrivals = []
    for _ in range(num):
        choice = rng.random()
        if choice < 0.35:
            pass
        elif choice < 0.5:
            time += rng.random() * 1.2 * time_period_in_secs
        else:
            time += rng.random() * 0.12 * time_period_in_secs
        arrivals.append(time)
    return arrivals


def max_starts_in_any_period(starts: Sequence[float], time_period_in_secs: float) -> int:
    """The largest number of starts within any half-open window of one time period."""
    ordered = sorted(starts)
    return max(
        sum(1 for other in ordered[i:] if other < start + time_period_in_secs - EPS)
        for i, start in enumerate(ordered)
    )


def max_leaky_bucket_excess(
    starts: Sequence[float],
    burst_size: int,
    requests_per_second: float,
) -> float:
    """How far the starts exceed the leaky-bucket bound ``burst_size + rate * t`` (at most 0)."""
    ordered = sorted(starts)
    return max(
        (j - i + 1) - (burst_size + requests_per_second * (ordered[j] - ordered[i]))
        for i in range(len(ordered))
        for j in range(i, len(ordered))
    )


def max_spacing_while_waiting(arrivals: Sequence[float], starts: Sequence[float]) -> float:
    """The largest spacing between starts while the next request was already waiting."""
    spacings = [
        starts[i] - starts[i - 1]
        for i in range(1, len(starts))
        if arrivals[i] <= starts[i - 1] + EPS
    ]
    return max(spacings, default=0.0)
