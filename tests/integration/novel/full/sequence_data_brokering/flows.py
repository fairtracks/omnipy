from omnipy.components.remote.models import HttpUrlModel
from omnipy.compute.flow import DagFlowTemplate, LinearFlowTemplate

from .models import SubmissionModel
from .tasks import (
    allocate_sequence_depot_submission_id,
    collect_submission_model,
    explode_submission_model,
    finalize_sequence_depot_submission,
    register_all_samples_with_biosamplevault,
    transfer_all_files,
)


@DagFlowTemplate(
    explode_submission_model,
    register_all_samples_with_biosamplevault.refine(
        param_key_map={'dataset': 'samples'},
        result_key='samples',
    ),
    collect_submission_model,
    consume_kwargs_from_results=False,
)
async def coordinate_biosamplevault_registration(
    submission: SubmissionModel,
    *,
    biosample_vault_url: HttpUrlModel,
) -> SubmissionModel: ...


@DagFlowTemplate(
    explode_submission_model,
    transfer_all_files.refine(
        param_key_map={'dataset': 'files'},
        result_key='files',
    ),
    collect_submission_model,
    consume_kwargs_from_results=False,
)
async def coordinate_external_file_transfer(
    submission: SubmissionModel,
    *,
    file_transfer_url: HttpUrlModel,
) -> SubmissionModel: ...


@LinearFlowTemplate(
    allocate_sequence_depot_submission_id,
    coordinate_biosamplevault_registration,
    coordinate_external_file_transfer,
    finalize_sequence_depot_submission,
)
async def broker_sequence_submission_flow(
    submission: SubmissionModel,
    *,
    sequence_depot_url: HttpUrlModel,
    biosample_vault_url: HttpUrlModel,
    file_transfer_url: HttpUrlModel,
) -> SubmissionModel: ...
