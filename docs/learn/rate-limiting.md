# Rate limiting of HTTP requests

When Omnipy fetches data over HTTP, for instance with `Dataset.load()` from a set of URLs, it
limits the requests to each host to `requests_per_time_period` requests per `time_period_in_secs`
seconds. Both are configured per host, together with a `burst_ratio`.

## What is guaranteed

With R requests per P seconds and a burst size B:

- **Never more than R requests start within P seconds**, wherever that period is placed. Servers
  count requests per fixed or sliding period, and the limit holds for both.
- **Small requests are answered quickly.** Up to B requests start at once when the host has not
  been busy for a while. B is the burst ratio times R, rounded down, and at least 1. More
  precisely, at most B + (R/P)·t requests start within any interval of length t, as with a leaky
  bucket.
- **No pauses while requests are waiting.** After a burst, the pace slows down and later returns to
  R per P seconds, but the requests keep being started. Long-running loads never look stuck.
- **Nothing is dropped.** Requests start in the order they arrive. Retries wait in line like any
  other request, and the timeout of each request counts from its actual start.

## How it works

Picture a small contraption. Requests waiting to start are balls in a bucket. A valve at the bottom
of the bucket lets them out one at a time into a pipe that takes P seconds to pass through. The pipe
clogs if it holds more than R balls: that is the server's limit. A camera watches the pipe, and a
controller sets the valve from what the camera sees.

- While fewer than B balls are in the pipe, the valve is fully open: this is the burst.
- Otherwise, the controller sets the valve so that the pipe fills up exactly when the ball that
  limits it leaves at the far end. For every ball in the pipe, it calculates the spacing at which
  evenly spaced releases, starting from the previous release, would fill the pipe exactly as that
  ball leaves:

    ```text
    spacing = (time the ball leaves - previous release) / (free places + m)
    ```

  where m counts the balls in the order they leave. The largest of these spacings is the fastest
  pace that never runs into a full pipe. It is never shorter than P/R.
- The setting holds until the ball that set it has left the pipe, a ball comes later than the
  setting allows, or a burst happens. Only then is a new one calculated. When several balls give
  the same spacing, the one that leaves last sets it, so that a setting lasts as long as possible.
  For a large batch of requests, a new setting is thus calculated about once per R requests.

## Try it

The simulation below shows the contraption at work for a few typical patterns of requests, for
R = 10 requests per P = 0.5 seconds. Step through the releases to see how the controller sets the
valve, and change the burst ratio to see its effect.

<iframe src="../rate-limiting-simulation.html" title="Rate limiting simulation" style="width: 100%; height: 1750px; border: 0;"></iframe>

[Open the simulation on its own page](rate-limiting-simulation.html).

## Configuration

The settings live in the runtime configuration, with defaults for all hosts and settings for
individual hosts:

```python
import omnipy as om

host_config = om.runtime.config.data.http.for_host['rest.ensembl.org']
host_config.requests_per_time_period = 15
host_config.time_period_in_secs = 1
host_config.burst_ratio = 0.3
```

- `requests_per_time_period`: a whole number, at least 1 (default 60).
- `time_period_in_secs`: a positive number of seconds (default 60).
- `burst_ratio`: strictly between 0 and 1 (default 0.5). With a ratio close to 1, the requests
  after a burst have to be spread over very little room, so the pace after a burst becomes slow.

The same configuration holds the settings for retries: `retry_http_statuses`, `retry_attempts` and
`retry_backoff_strategy`.

## Current limitations

- The limit applies per load: two loads that run at the same time against the same host each get
  the full rate.
- A host that answers with 429 (Too Many Requests) is retried like other failures. Its
  `Retry-After` header is not yet taken into account, and a host that is down does not yet stop
  the whole load early.
