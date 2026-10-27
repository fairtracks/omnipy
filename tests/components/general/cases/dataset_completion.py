"""Dataset task markers and expected completion-check errors."""

import pytest_cases as pc

from omnipy.data.helpers import FailedData, PendingData


@pc.case
def case_pending() -> tuple[dict[str, PendingData | FailedData], str]:
    return (
        {'waiting': PendingData(job_name='fetch')},
        "Incomplete batch: failed=(), pending=('waiting',)",
    )


@pc.case
def case_failed() -> tuple[dict[str, PendingData | FailedData], str]:
    return (
        {'broken': FailedData(job_name='fetch', exception=ValueError('Fetch failed'))},
        "Incomplete batch: failed=('broken',), pending=()",
    )


@pc.case
def case_mixed() -> tuple[dict[str, PendingData | FailedData], str]:
    return (
        {
            'broken': FailedData(job_name='fetch', exception=ValueError('Fetch failed')),
            'waiting': PendingData(job_name='fetch'),
            'also_broken': FailedData(job_name='parse', exception=ValueError('Parse failed')),
        },
        "Incomplete batch: failed=('broken', 'also_broken'), pending=('waiting',)",
    )
