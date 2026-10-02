import asyncio
from typing import Annotated, cast

import pytest

from omnipy.compute.flow import FuncFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.data.model import Model
from omnipy.shared.enums.job import RunState

from .....engine.helpers.functions import assert_job_state
from .data import (build_biosamplevault_registration_request,
                   build_external_transfer_manifest,
                   build_sequence_depot_submission_id_request,
                   build_sequence_submission,
                   expected_sequence_depot_submission_payload)
from .helpers import (append_workflow_event,
                      assert_submission_ready_for_final_submission,
                      clone_submission)
from .models import SubmissionModel


async def test_sequence_submission_brokering(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
) -> None:
    submission = build_sequence_submission()
    print()
    submission.full(width=160)

    brokering_flow = broker_sequence_submission_flow.apply()
    final_submission = await brokering_flow(submission)

    assert final_submission.samples.to_data() == {
        'Sample-A': {
            'biosamplevault_sample_id': 'BSV-SAMPLE-A',
            'collection_site': 'North Works',
            'local_sample_alias': 'sample-a',
            'local_submission_alias': 'sub-2026-alpha',
            'sampled_at': '2026-05-03',
            'specimen_type': 'wastewater solids'
        },
        'Sample-B': {
            'biosamplevault_sample_id': 'BSV-SAMPLE-B',
            'collection_site': 'River Mouth',
            'local_sample_alias': 'sample-b',
            'local_submission_alias': 'sub-2026-alpha',
            'sampled_at': '2026-05-10',
            'specimen_type': 'river grab'
        }
    }

    assert final_submission.files.to_data() == {
        'file-id-1': {
            'file_id': 'file-id-1',
            'file_name': 'sample-a_R1.fastq.gz',
            'file_role': 'read1',
            'local_sample_alias': 'sample-a',
            'local_submission_alias': 'sub-2026-alpha',
            'md5': 'md5-sample-a-r1',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA'
        },
        'file-id-2': {
            'file_id': 'file-id-2',
            'file_name': 'sample-a_R2.fastq.gz',
            'file_role': 'read2',
            'local_sample_alias': 'sample-a',
            'local_submission_alias': 'sub-2026-alpha',
            'md5': 'md5-sample-a-r2',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA'
        },
        'file-id-3': {
            'file_id': 'file-id-3',
            'file_name': 'sample-b_R1.fastq.gz',
            'file_role': 'read1',
            'local_sample_alias': 'sample-b',
            'local_submission_alias': 'sub-2026-alpha',
            'md5': 'md5-sample-b-r1',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA'
        },
        'file-id-4': {
            'file_id': 'file-id-4',
            'file_name': 'sample-b_R2.fastq.gz',
            'file_role': 'read2',
            'local_sample_alias': 'sample-b',
            'local_submission_alias': 'sub-2026-alpha',
            'md5': 'md5-sample-b-r2',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA'
        }
    }

    assert final_submission.metadata.to_data() == {
        'local_submission_alias':
            'sub-2026-alpha',
        'local_sample_aliases': ['sample-b', 'sample-a'],
        'project_code':
            'NORW-PATH-42',
        'study_title':
            'Northern waterways genomic surveillance pilot',
        'release_date':
            '2026-06-15',
        'submission_checklist_version':
            'ENA-CHECKLIST-1.0',
        'transfer_status':
            'completed-external',
        'archive_status':
            'submitted',
        'sequence_depot_submission_id':
            'SEQDEPOT-SUB-2026-ALPHA',
        'external_transfer_ticket':
            'XFER-SUB-2026-ALPHA',
        'final_receipt_message':
            'Submitted submission sub-2026-alpha to Sequence Depot',
        'workflow_events': [
            'metadata_normalized',
            'storage_manifest_verified',
            'sequence_depot_submission_id_allocated',
            'external_transfer_completed',
            'biosamplevault_samples_registered',
            'sequence_depot_submission_finalized',
        ],
    }

    assert build_external_transfer_manifest(final_submission) == {
        'local_submission_alias':
            'sub-2026-alpha',
        'files': [
            {
                'local_sample_alias': 'sample-a',
                'file_role': 'read1',
                'file_name': 'sample-a_R1.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
                'md5': 'md5-sample-a-r1',
            },
            {
                'local_sample_alias': 'sample-a',
                'file_role': 'read2',
                'file_name': 'sample-a_R2.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
                'md5': 'md5-sample-a-r2',
            },
            {
                'local_sample_alias': 'sample-b',
                'file_role': 'read1',
                'file_name': 'sample-b_R1.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
                'md5': 'md5-sample-b-r1',
            },
            {
                'local_sample_alias': 'sample-b',
                'file_role': 'read2',
                'file_name': 'sample-b_R2.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
                'md5': 'md5-sample-b-r2',
            },
        ],
    }

    assert build_sequence_depot_submission_id_request(final_submission) == {
        'local_submission_alias': 'sub-2026-alpha',
        'project_code': 'NORW-PATH-42',
        'local_sample_aliases': Model[list[str]](['sample-b', 'sample-a']),
    }
    assert build_biosamplevault_registration_request(final_submission) == [
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-a',
            'specimen_type': 'wastewater solids',
            'collection_site': 'North Works',
            'sampled_at': '2026-05-03',
        },
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-b',
            'specimen_type': 'river grab',
            'collection_site': 'River Mouth',
            'sampled_at': '2026-05-10',
        },
    ]
    assert final_submission.to_data() == \
        expected_sequence_depot_submission_payload()

    assert_job_state(brokering_flow, [RunState.FINISHED])


@TaskTemplate()
def normalize_submission(submission: SubmissionModel) -> SubmissionModel:
    # validate_submission_linkage(submission)
    return append_workflow_event(clone_submission(submission), 'metadata_normalized')


@TaskTemplate()
async def verify_storage_manifest(submission: SubmissionModel) -> SubmissionModel:
    await asyncio.sleep(0)

    files = submission.files.values()
    assert all(cast(str, file_row.storage_uri).startswith('s3://') for file_row in files)
    assert all(cast(str, file_row.md5).startswith('md5-') for file_row in files)

    submission.metadata.archive_status = 'files-verified'
    return append_workflow_event(submission, 'storage_manifest_verified')


@TaskTemplate()
async def allocate_sequence_depot_submission_id(submission: SubmissionModel) -> SubmissionModel:
    await asyncio.sleep(0)

    request_payload = build_sequence_depot_submission_id_request(submission)
    submission.metadata.sequence_depot_submission_id = 'SEQDEPOT-SUB-2026-ALPHA'

    submission_with_event = append_workflow_event(
        submission,
        'sequence_depot_submission_id_allocated',
    )

    assert request_payload == {
        'local_submission_alias': submission.metadata.local_submission_alias,
        'project_code': submission.metadata.project_code,
        'local_sample_aliases': submission.metadata.local_sample_aliases,
    }

    return submission_with_event


@TaskTemplate()
async def coordinate_external_transfer(submission: SubmissionModel) -> SubmissionModel:
    await asyncio.sleep(0)

    transfer_manifest = build_external_transfer_manifest(submission)
    assert transfer_manifest['local_submission_alias'] == 'sub-2026-alpha'

    for file_row in submission.files.values():
        file_row.transfer_ticket = 'XFER-SUB-2026-ALPHA'

    submission.metadata.transfer_status = 'completed-external'
    submission.metadata.external_transfer_ticket = 'XFER-SUB-2026-ALPHA'

    return append_workflow_event(submission, 'external_transfer_completed')


@TaskTemplate()
async def register_samples_with_biosamplevault(submission: SubmissionModel) -> SubmissionModel:
    await asyncio.sleep(0)

    registration_request = build_biosamplevault_registration_request(submission)
    for sample in submission.samples.values():
        sample_alias = sample.local_sample_alias
        sample.biosamplevault_sample_id = f'BSV-{sample_alias.upper()}'

    submission.metadata.archive_status = 'samples-registered'

    submission_with_event = append_workflow_event(
        submission,
        'biosamplevault_samples_registered',
    )

    assert registration_request == [
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-a',
            'specimen_type': 'wastewater solids',
            'collection_site': 'North Works',
            'sampled_at': '2026-05-03',
        },
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-b',
            'specimen_type': 'river grab',
            'collection_site': 'River Mouth',
            'sampled_at': '2026-05-10',
        },
    ]

    return submission_with_event


@TaskTemplate()
async def finalize_sequence_depot_submission(submission: SubmissionModel) -> SubmissionModel:
    await asyncio.sleep(0)

    assert submission.metadata.sequence_depot_submission_id == 'SEQDEPOT-SUB-2026-ALPHA'
    # assert submission.metadata.transfer_status == 'completed-external'

    submission.metadata.archive_status = 'submitted'
    submission.metadata.final_receipt_message = (
        'Submitted submission sub-2026-alpha to Sequence Depot')

    submitted_submission = append_workflow_event(
        submission,
        'sequence_depot_submission_finalized',
    )
    assert_submission_ready_for_final_submission(submitted_submission)
    assert submitted_submission.to_data() == expected_sequence_depot_submission_payload()
    return submitted_submission


@FuncFlowTemplate()
async def broker_sequence_submission_flow(submission: SubmissionModel) -> SubmissionModel:
    normalized_submission = normalize_submission(submission)
    verified_submission = await verify_storage_manifest(normalized_submission)
    submission_with_submission_id = await allocate_sequence_depot_submission_id(verified_submission)
    transferred_submission = await coordinate_external_transfer(submission_with_submission_id)
    sample_registered_submission = await register_samples_with_biosamplevault(transferred_submission
                                                                              )
    return await finalize_sequence_depot_submission(sample_registered_submission)
