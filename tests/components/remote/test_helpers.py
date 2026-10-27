"""Tests for remote helper utilities."""

import asyncio
from collections.abc import AsyncGenerator
import copy
import json
from pathlib import Path
import random
import re
from typing import Annotated

from aiohttp import ClientTimeout, web
import pytest
import pytest_cases as pc

from omnipy.components.remote.helpers import (
    FLOAT_TOLERANCE,
    RateLimiter,
    RateLimitingClientSession,
    RequestPacer,
)
from omnipy.components.remote.tasks import get_retry_client

from .helpers.pacing import (
    max_leaky_bucket_excess,
    max_spacing_while_waiting,
    max_starts_in_any_period,
    pacer_start_times,
    per_ball_start_times,
    random_arrivals,
)


async def my_endpoint(request: web.Request) -> web.Response:
    """Return a simple JSON response for rate-limiting tests."""
    return web.json_response('My response')


def create_app() -> web.Application:
    """Create the aiohttp app used by rate-limiting tests."""
    app = web.Application()
    app.router.add_route('GET', '/my_endpoint', my_endpoint)
    return app


@pc.fixture(scope='function')
async def my_endpoint_url(aiohttp_server) -> AsyncGenerator[str, None]:
    server = await aiohttp_server(create_app())
    yield str(server.make_url('/my_endpoint'))


async def _assert_requests_and_get_run_time_in_secs(
    client_session: RateLimitingClientSession,
    my_endpoint_url: str,
    num_requests: int,
) -> float:
    """Assert successful responses and return the total run time."""
    # The monotonic clock of the event loop, as the wall clock can be adjusted during the test
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    tasks = [client_session.get(my_endpoint_url) for _ in range(num_requests)]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        assert response.status == 200
        assert await response.text() == '"My response"'

    return loop.time() - start_time


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'num_requests, requests_per_time_period, time_period_in_secs, run_time_min, run_time_max',
    [
        (21, 1, 0.05, 1.0, 1.2),
        (21, 10, 0.5, 1.0, 1.2),
    ],
    ids=['no_burst_1_requests_per_0.05s', 'burst_10_requests_per_0.5s'],
)
async def test_rate_limiting_client_session(
    my_endpoint_url: Annotated[str, pytest.fixture],
    num_requests: int,
    requests_per_time_period: int,
    time_period_in_secs: float,
    run_time_min: float,
    run_time_max: float,
) -> None:
    client_session = RateLimitingClientSession(requests_per_time_period, time_period_in_secs)

    async with client_session:
        assert client_session.requests_per_second == requests_per_time_period / time_period_in_secs

        for i in range(2):
            run_time = await _assert_requests_and_get_run_time_in_secs(
                client_session,
                my_endpoint_url,
                num_requests,
            )

            assert run_time_min < run_time < run_time_max

            await asyncio.sleep(0.1)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'requests_per_time_period, time_period_in_secs, secs_between_requests',
    [
        pytest.param(10, 0.5, 0, id='all_at_once'),
        pytest.param(10, 0.5, 0.01, id='staggered_100_per_s'),
        pytest.param(10, 0.5, 0.03, id='staggered_33_per_s'),
        pytest.param(1, 0.05, 0.01, id='no_burst_staggered'),
    ],
)
async def test_rate_limiting_client_session_never_exceeds_rate_in_any_time_period(
    my_endpoint_url: Annotated[str, pytest.fixture],
    monkeypatch: pytest.MonkeyPatch,
    requests_per_time_period: int,
    time_period_in_secs: float,
    secs_between_requests: float,
) -> None:
    # The start time of each request is recorded when the session lets the request through. This
    # avoids the varying delays of the network, e.g. for connecting under heavy load
    start_times: list[float] = []
    wait = RateLimiter.wait

    async def recording_wait(self: RateLimiter) -> None:
        await wait(self)
        start_times.append(asyncio.get_running_loop().time())

    monkeypatch.setattr(RateLimiter, 'wait', recording_wait)

    async def request_after_delay(session: RateLimitingClientSession, delay: float) -> None:
        await asyncio.sleep(delay)
        async with session.get(my_endpoint_url) as response:
            assert response.status == 200

    num_requests = 4 * requests_per_time_period + 1

    async with RateLimitingClientSession(requests_per_time_period, time_period_in_secs) as session:
        await asyncio.gather(
            *[request_after_delay(session, i * secs_between_requests) for i in range(num_requests)]
        )

    assert len(start_times) == num_requests

    # The recorded times can be off by some milliseconds when the machine is busy, which is
    # allowed for by testing against a slightly shorter time period
    tested_period = time_period_in_secs * 0.9
    for i, start_time in enumerate(start_times):
        num_in_period = sum(1 for t in start_times[i:] if t < start_time + tested_period)
        assert num_in_period <= requests_per_time_period

    # Apart from the initial burst, requests are spread out and not started in groups
    for i, start_time in enumerate(start_times):
        if start_time > start_times[0] + time_period_in_secs:
            num_in_group = sum(1 for t in start_times[i:] if t < start_time + 0.1 * tested_period)
            assert num_in_group <= 2

    # A burst of requests at once is followed by requests spread out evenly, without a long pause
    if secs_between_requests == 0:
        secs_between_starts = [b - a for a, b in zip(start_times, start_times[1:])]
        assert max(secs_between_starts) < 5 * time_period_in_secs / requests_per_time_period


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_rate_limiting_client_session_parameters() -> None:
    async with RateLimitingClientSession(10, 0.5, burst_ratio=0.3) as session:
        assert session.requests_per_time_period == 10
        assert session.time_period_in_secs == 0.5
        assert session.requests_per_second == 20
        assert session.burst_size == 3
    assert session.closed

    async with RateLimitingClientSession(10, 0.5) as session:
        assert session.burst_size == 5

    with pytest.raises(ValueError):
        RateLimitingClientSession(10, 0.5, burst_ratio=1.0)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_rate_limiting_client_session_request_methods(aiohttp_server) -> None:
    async def echo(request: web.Request) -> web.Response:
        body = await request.json() if request.can_read_body else None
        return web.json_response(
            dict(method=request.method, header=request.headers.get('X-Test'), body=body)
        )

    app = web.Application()
    app.router.add_route('*', '/echo', echo)
    url = str((await aiohttp_server(app)).make_url('/echo'))

    # Arguments other than the rate limiting ones are passed on to the aiohttp ClientSession
    async with RateLimitingClientSession(10, 0.5, headers={'X-Test': 'yes'}) as session:
        async with session.get(url) as response:
            assert await response.json() == dict(method='GET', header='yes', body=None)

        async with session.post(url, json=dict(a=1)) as response:
            assert await response.json() == dict(method='POST', header='yes', body=dict(a=1))

        async with session.request('PUT', url, json=[1, 2]) as response:
            assert await response.json() == dict(method='PUT', header='yes', body=[1, 2])

        # Requests can also be awaited directly, as aiohttp_retry does
        response = await session.request('GET', url)
        assert response.status == 200
        response.release()

        assert not session.closed

    assert session.closed


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_rate_limiting_client_session_timeout_counts_from_start_of_request(
    aiohttp_server,
) -> None:
    # A request that waits for the rate limiter must still time out, counting from its own start

    async def slow_endpoint(request: web.Request) -> web.Response:
        await asyncio.sleep(1.5)
        return web.json_response('Too late')

    app = web.Application()
    app.router.add_route('GET', '/slow', slow_endpoint)
    url = str((await aiohttp_server(app)).make_url('/slow'))

    loop = asyncio.get_running_loop()
    async with RateLimitingClientSession(1, 0.4, timeout=ClientTimeout(total=0.3)) as session:
        start = loop.time()

        async def time_until_timeout() -> float | None:
            try:
                async with session.get(url) as response:
                    await response.text()
            except TimeoutError:
                return loop.time() - start
            return None

        timed_out_after = await asyncio.gather(*[time_until_timeout() for _ in range(3)])

    # The requests start at 0.0, 0.4 and 0.8 s, and each times out 0.3 s later
    assert None not in timed_out_after
    assert sorted(t for t in timed_out_after if t is not None) == pytest.approx(
        [0.3, 0.7, 1.1], abs=0.1
    )


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_rate_limiting_client_session_paces_retries(aiohttp_server) -> None:
    # Each retry attempt is a request to the host, so it waits for the rate limiter as well
    loop = asyncio.get_running_loop()
    arrival_times: list[float] = []

    async def fails_once(request: web.Request) -> web.Response:
        arrival_times.append(loop.time())
        if len(arrival_times) == 1:
            return web.Response(text='Error', status=503)
        return web.json_response('Recovered')

    app = web.Application()
    app.router.add_route('GET', '/fails_once', fails_once)
    url = str((await aiohttp_server(app)).make_url('/fails_once'))

    async with RateLimitingClientSession(1, 0.3) as session:
        async with get_retry_client(
            client_session=session,
            retry_http_statuses=(503,),
            retry_attempts=2,
        ) as retry_client:
            async with retry_client.get(url) as response:
                assert response.status == 200
                assert await response.json() == 'Recovered'

    assert len(arrival_times) == 2
    assert arrival_times[1] - arrival_times[0] >= 0.3 - 0.02


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_rate_limiter_starts_waiting_requests_in_order() -> None:
    limiter = RateLimiter(10, 0.5)
    loop = asyncio.get_running_loop()
    start = loop.time()
    order: list[int] = []
    start_times: list[float] = []

    async def wait_and_record(i: int) -> None:
        await limiter.wait()
        order.append(i)
        start_times.append(loop.time() - start)

    await asyncio.gather(*[wait_and_record(i) for i in range(21)])

    assert order == list(range(21))
    expected = [0.0] * 5 + [0.5 / 6 * k for k in range(1, 6)] + [0.5 + 0.05 * k for k in range(11)]
    assert start_times == pytest.approx(expected, abs=0.05)
    # Timers never fire early
    assert all(t >= e - 0.002 for t, e in zip(start_times, expected))


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
async def test_rate_limiter_cancelled_wait_does_not_delay_the_next_request() -> None:
    limiter = RateLimiter(1, 0.3)
    loop = asyncio.get_running_loop()
    start = loop.time()
    await limiter.wait()

    waiting = asyncio.create_task(limiter.wait())
    await asyncio.sleep(0.05)
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting

    await limiter.wait()
    assert loop.time() - start == pytest.approx(0.3, abs=0.05)


# Pacing rule (RequestPacer), without asyncio. See
# docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-design.md


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'requests_per_time_period, burst_ratio, burst_size',
    [
        (10, 0.5, 5),
        (10, 0.3, 3),
        (10, 0.7, 7),
        (10, 0.05, 1),
        (3, 0.9, 2),
        (100, 0.29, 29),
        (1, 0.5, 1),
        (1, 0.99, 1),
    ],
)
def test_request_pacer_burst_size(
    requests_per_time_period: int,
    burst_ratio: float,
    burst_size: int,
) -> None:
    pacer = RequestPacer(requests_per_time_period, 0.5, burst_ratio=burst_ratio)
    assert pacer.burst_size == burst_size
    assert pacer.requests_per_time_period == requests_per_time_period
    assert pacer.time_period_in_secs == 0.5
    assert pacer.requests_per_second == requests_per_time_period / 0.5


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_request_pacer_default_burst_ratio() -> None:
    assert RequestPacer(10, 0.5).burst_size == 5


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'requests_per_time_period, time_period_in_secs, burst_ratio',
    [
        (0, 0.5, 0.5),
        (-1, 0.5, 0.5),
        (2.5, 0.5, 0.5),
        (True, 0.5, 0.5),
        (10, 0, 0.5),
        (10, -0.5, 0.5),
        (10, 0.5, 0),
        (10, 0.5, 1),
        (10, 0.5, -0.1),
        (10, 0.5, 1.5),
    ],
)
def test_request_pacer_rejects_invalid_parameters(
    requests_per_time_period: int,
    time_period_in_secs: float,
    burst_ratio: float,
) -> None:
    with pytest.raises(ValueError):
        RequestPacer(requests_per_time_period, time_period_in_secs, burst_ratio=burst_ratio)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'requests_per_time_period, time_period_in_secs, burst_ratio, arrivals, expected_starts',
    [
        pytest.param(
            10,
            0.5,
            0.5,
            [0.0] * 21,
            [0.0] * 5 + [0.5 / 6 * k for k in range(1, 6)] + [0.5 + 0.05 * k for k in range(11)],
            id='burst_then_slower_then_steady',
        ),
        pytest.param(
            10,
            0.5,
            0.6,
            [0.0] + [0.3] * 5 + [0.4] * 8,
            [0.0] + [0.3] * 5 + [0.4, 0.48, 0.56, 0.64, 0.72, 0.8, 0.85, 0.9],
            id='late_request_starts_a_new_setting',
        ),
        pytest.param(
            10,
            0.5,
            0.6,
            [0.03 * k for k in range(21)],
            [0.03 * k for k in range(6)]
            + [0.15 + 0.07 * k for k in range(1, 6)]
            + [0.5 + 0.05 * k for k in range(1, 11)],
            id='arriving_faster_than_the_rate',
        ),
        pytest.param(1, 0.2, 0.5, [0.0] * 3, [0.0, 0.2, 0.4], id='one_request_per_period'),
        pytest.param(10, 0.5, 0.5, [5.0], [5.0], id='single_request'),
        pytest.param(10, 0.5, 0.5, [0.0] * 3, [0.0] * 3, id='small_request_within_burst'),
    ],
)
def test_request_pacer_start_times(
    requests_per_time_period: int,
    time_period_in_secs: float,
    burst_ratio: float,
    arrivals: list[float],
    expected_starts: list[float],
) -> None:
    pacer = RequestPacer(requests_per_time_period, time_period_in_secs, burst_ratio=burst_ratio)
    assert pacer_start_times(pacer, arrivals) == pytest.approx(expected_starts, abs=FLOAT_TOLERANCE)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'requests_per_time_period, time_period_in_secs, burst_ratio, arrivals',
    [
        # A start leaves the window exactly when the next request is ready
        pytest.param(2, 1.0, 0.5, [0.0, 1.0], id='start_leaves_window_exactly_when_ready'),
        pytest.param(2, 1.0, 0.5, [0.0, 0.999], id='start_still_in_window_when_ready'),
        # A request that is ready exactly at its earliest start is not late
        pytest.param(10, 0.5, 0.5, [0.0] * 6 + [0.5 / 6 * 2] * 5, id='ready_exactly_on_time'),
        # After a backlog has drained, a new batch gets the full burst again
        pytest.param(10, 0.5, 0.5, [0.0] * 21 + [10.0] * 6, id='new_burst_after_idle'),
        # A pause shorter than the period does not give a new burst
        pytest.param(
            10,
            0.5,
            0.5,
            [0.05 * k for k in range(12)] + [0.65] * 10,
            id='no_new_burst_after_short_pause',
        ),
        pytest.param(10, 0.5, 0.9, [0.0] * 30, id='large_burst_ratio'),
        pytest.param(60, 60.0, 0.5, [0.0] * 100, id='default_host_configuration'),
    ],
)
def test_request_pacer_border_cases_match_per_ball_calculation(
    requests_per_time_period: int,
    time_period_in_secs: float,
    burst_ratio: float,
    arrivals: list[float],
) -> None:
    pacer = RequestPacer(requests_per_time_period, time_period_in_secs, burst_ratio=burst_ratio)
    starts = pacer_start_times(pacer, arrivals)
    expected = per_ball_start_times(
        arrivals, requests_per_time_period, time_period_in_secs, pacer.burst_size
    )
    assert starts == pytest.approx(expected, abs=FLOAT_TOLERANCE)
    assert max_starts_in_any_period(starts, time_period_in_secs) <= requests_per_time_period


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_request_pacer_new_burst_after_idle() -> None:
    pacer = RequestPacer(10, 0.5, burst_ratio=0.5)
    starts = pacer_start_times(pacer, [0.0] * 21 + [10.0] * 6)
    assert starts[21:] == pytest.approx([10.0] * 5 + [10.0 + 0.5 / 6], abs=FLOAT_TOLERANCE)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_request_pacer_plan_start_does_not_change_state() -> None:
    # A request that is cancelled after planning its start must not affect the next ones
    pacer = RequestPacer(10, 0.5, burst_ratio=0.5)
    untouched_pacer = RequestPacer(10, 0.5, burst_ratio=0.5)
    pacer_start_times(pacer, [0.0] * 5)
    pacer_start_times(untouched_pacer, [0.0] * 5)
    state = copy.deepcopy(vars(pacer))

    # Plans calculating a new spacing, and for a request that is not ready in time
    pacer.plan_start(0.0)
    pacer.plan_start(0.3)
    assert vars(pacer) == state

    arrivals = [0.01] + [0.3] * 10
    assert pacer_start_times(pacer, arrivals) == pacer_start_times(untouched_pacer, arrivals)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_request_pacer_rejects_misused_plans() -> None:
    pacer = RequestPacer(10, 0.5, burst_ratio=0.5)
    pacer_start_times(pacer, [0.0] * 5)

    plan = pacer.plan_start(0.0)
    with pytest.raises(ValueError, match='before its plan'):
        pacer.record_start(plan, plan.start - 0.01)

    pacer.record_start(plan, plan.start)
    with pytest.raises(ValueError, match='not based on the latest start'):
        pacer.record_start(plan, plan.start)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize('requests_per_time_period', [1, 2, 4, 10, 20, 60])
@pytest.mark.parametrize('burst_ratio', [0.3, 0.5, 0.7, 0.9])
def test_request_pacer_matches_per_ball_calculation_and_keeps_guarantees(
    requests_per_time_period: int,
    burst_ratio: float,
) -> None:
    time_period_in_secs = 0.5
    rng = random.Random(requests_per_time_period * 1000 + int(burst_ratio * 10))
    for _ in range(20):
        pacer = RequestPacer(requests_per_time_period, time_period_in_secs, burst_ratio=burst_ratio)
        arrivals = random_arrivals(rng, 3 * requests_per_time_period + 10, time_period_in_secs)
        starts = pacer_start_times(pacer, arrivals)

        expected = per_ball_start_times(
            arrivals, requests_per_time_period, time_period_in_secs, pacer.burst_size
        )
        assert starts == pytest.approx(expected, abs=1e-7)

        # Requests start in order, never before they arrive
        assert all(start >= arrival for start, arrival in zip(starts, arrivals))
        assert starts == sorted(starts)

        # Window bound: at most R starts in any time period
        assert max_starts_in_any_period(starts, time_period_in_secs) <= requests_per_time_period

        # Leaky-bucket bound: at most B + R/P * t starts in any interval t
        assert (
            max_leaky_bucket_excess(starts, pacer.burst_size, pacer.requests_per_second)
            <= FLOAT_TOLERANCE
        )

        # No gaps: while requests wait, the spacing never exceeds the ramp after a full burst
        max_spacing = time_period_in_secs / (requests_per_time_period - pacer.burst_size + 1)
        assert max_spacing_while_waiting(arrivals, starts) <= max_spacing + FLOAT_TOLERANCE


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize('requests_per_time_period', [1, 4, 10, 20])
def test_request_pacer_keeps_guarantees_when_requests_start_late(
    requests_per_time_period: int,
) -> None:
    # When the event loop is busy, requests start later than planned
    time_period_in_secs = 0.5
    rng = random.Random(requests_per_time_period)
    for _ in range(20):
        pacer = RequestPacer(requests_per_time_period, time_period_in_secs)
        arrivals = random_arrivals(rng, 3 * requests_per_time_period + 10, time_period_in_secs)
        delays = [
            rng.random() * 0.3 * time_period_in_secs if rng.random() < 0.2 else 0.0
            for _ in arrivals
        ]
        starts = pacer_start_times(pacer, arrivals, delays)

        assert max_starts_in_any_period(starts, time_period_in_secs) <= requests_per_time_period
        assert (
            max_leaky_bucket_excess(starts, pacer.burst_size, pacer.requests_per_second)
            <= FLOAT_TOLERANCE
        )


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
@pytest.mark.parametrize(
    'requests_per_time_period, time_period_in_secs',
    [(10, 0.5), (60, 60.0)],
)
def test_request_pacer_calculates_spacing_once_per_segment(
    monkeypatch: pytest.MonkeyPatch,
    requests_per_time_period: int,
    time_period_in_secs: float,
) -> None:
    # In a steady backlog, a valve setting holds for a whole time period
    num_calculations = 0
    calculate_spacing = RequestPacer._calculate_spacing

    def counting_calculate_spacing(self: RequestPacer, *args, **kwargs):
        nonlocal num_calculations
        num_calculations += 1
        return calculate_spacing(self, *args, **kwargs)

    monkeypatch.setattr(RequestPacer, '_calculate_spacing', counting_calculate_spacing)

    num_requests = 1000
    pacer = RequestPacer(requests_per_time_period, time_period_in_secs)
    pacer_start_times(pacer, [0.0] * num_requests)
    assert num_calculations <= num_requests // requests_per_time_period + 2


DOCS_SIMULATION_PATH = (
    Path(__file__).parents[3] / 'docs' / 'learn' / 'rate-limiting-simulation.html'
)


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_request_pacer_matches_the_simulation_in_the_docs() -> None:
    # The simulation in the docs has its own (JavaScript) model of the pacing. It records the
    # start times it computes, and checks itself against them when the page loads
    match = re.search(
        r'<script type="application/json" id="recorded-start-times">\s*(.*?)\s*</script>',
        DOCS_SIMULATION_PATH.read_text(),
        re.DOTALL,
    )
    assert match is not None
    recorded = json.loads(match.group(1))
    assert len(recorded) >= 20

    for entry in recorded:
        pacer = RequestPacer(10, 0.5, burst_ratio=entry['burst_ratio'])
        assert pacer.burst_size == entry['burst_size']
        starts = pacer_start_times(pacer, entry['arrivals'])
        assert starts == pytest.approx(entry['starts'], abs=FLOAT_TOLERANCE), entry['scenario']
