from typing import Annotated

import pytest

from omnipy.shared.enums.job import RunState

from .....engine.helpers.functions import assert_job_state
from .flows import broker_sequence_submission_flow
from .models import SubmissionModel


@pytest.mark.usefixtures('runtime_all_engines', 'reset_biosample_vault_sample_id_generator')
async def test_sequence_submission_brokering(
    samples: Annotated[dict[str, dict[str, str]], pytest.fixture],
    files: Annotated[dict[str, dict[str, str]], pytest.fixture],
    metadata: Annotated[dict[str, str], pytest.fixture],
    expected_sequence_depot_submission_payload: Annotated[dict[str, object], pytest.fixture],
) -> None:
    submission = SubmissionModel(samples=samples, files=files, metadata=metadata)

    print()
    print('Input submission:')
    submission.full(width=160)

    brokering_flow = broker_sequence_submission_flow.apply()
    completed_submission = await brokering_flow(submission)

    assert completed_submission.to_data() == expected_sequence_depot_submission_payload

    assert_job_state(brokering_flow, [RunState.FINISHED])

    print()
    print('Completed submission:')
    completed_submission.full(width=160)
