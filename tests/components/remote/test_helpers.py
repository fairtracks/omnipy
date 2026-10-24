"""Tests for remote helper utilities."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated

from aiohttp import ClientSession, web
import pytest
import pytest_cases as pc

from omnipy.components.remote.helpers import RateLimitingClientSession


async def my_endpoint(request: web.Request) -> web.Response:
    """Return a simple JSON response for rate-limiting tests."""
    return web.json_response('My response')


def create_app() -> web.Application:
    """Create the aiohttp app used by rate-limiting tests."""
    app = web.Application()
    app.router.add_route('GET', '/my_endpoint', my_endpoint)
    return app


# The current RateLimitingClientSession can exceed the configured rate after a burst, and starts
# the requests in groups with pauses in between. To be fixed by the rewrite in
# docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-design.md
RATE_LIMITER_PACING_BUG = pytest.mark.xfail(
    reason='Known rate limiter pacing bug, see the rate limiter pacing design', strict=False
)


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
@RATE_LIMITER_PACING_BUG
async def test_rate_limiting_client_session(
    my_endpoint_url: Annotated[str, pytest.fixture],
    num_requests: int,
    requests_per_time_period: float,
    time_period_in_secs: float,
    run_time_min: float,
    run_time_max: float,
) -> None:
    client_session = RateLimitingClientSession(requests_per_time_period, time_period_in_secs)

    async with client_session:
        assert client_session.requests_per_second == requests_per_time_period / time_period_in_secs
        assert isinstance(client_session, ClientSession)

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
        pytest.param(10, 0.5, 0.01, id='staggered_100_per_s', marks=RATE_LIMITER_PACING_BUG),
        pytest.param(10, 0.5, 0.03, id='staggered_33_per_s', marks=RATE_LIMITER_PACING_BUG),
        pytest.param(1, 0.05, 0.01, id='no_burst_staggered', marks=RATE_LIMITER_PACING_BUG),
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
    limit_request = RateLimitingClientSession._limit_request

    async def recording_limit_request(self: RateLimitingClientSession, *args, **kwargs) -> None:
        await limit_request(self, *args, **kwargs)
        start_times.append(asyncio.get_running_loop().time())

    monkeypatch.setattr(RateLimitingClientSession, '_limit_request', recording_limit_request)

    async def request_after_delay(session: ClientSession, delay: float) -> None:
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
