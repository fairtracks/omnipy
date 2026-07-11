import asyncio
from inspect import isawaitable
from typing import Annotated
from typing import cast

import pytest

from omnipy import FuncFlowTemplate, TaskTemplate
from omnipy.shared.enums.job import RunState

from ....engine.helpers.functions import assert_job_state
from .helpers.submission_cases import (build_biosamplevault_registration_request,
                                       build_external_transfer_manifest,
                                       build_sequence_depot_submission_id_request,
                                       build_sequence_submission_package,
                                       build_sequence_depot_submission_payload,
                                       expected_sequence_depot_submission_payload)
from .helpers.submission_models import (SubmissionPackage,
                                        append_workflow_event,
                                        assert_submission_ready_for_final_submission,
                                        clone_submission_package,
                                        update_submission_files,
                                        update_submission_metadata,
                                        update_submission_samples,
                                        validate_submission_linkage)


async def test_sequence_submission_brokering(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
) -> None:
    submission_package = build_sequence_submission_package()

    brokering_flow = broker_sequence_submission_flow.apply()
    final_package_result = brokering_flow(submission_package)
    final_package = await final_package_result if isawaitable(final_package_result) else final_package_result

    assert set(final_package.keys()) == {
        'submission_samples',
        'submission_files',
        'submission_metadata',
    }

    assert cast(list[dict[str, object]], final_package['submission_samples'].to_data()) == [
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-a',
            'specimen_type': 'wastewater solids',
            'collection_site': 'North Works',
            'sampled_at': '2026-05-03',
            'biosamplevault_sample_id': 'BSV-SAMPLE-A',
        },
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-b',
            'specimen_type': 'river grab',
            'collection_site': 'River Mouth',
            'sampled_at': '2026-05-10',
            'biosamplevault_sample_id': 'BSV-SAMPLE-B',
        },
    ]

    assert cast(list[dict[str, object]], final_package['submission_files'].to_data()) == [
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-a',
            'file_role': 'read1',
            'file_name': 'sample-a_R1.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
            'md5': 'md5-sample-a-r1',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA',
        },
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-a',
            'file_role': 'read2',
            'file_name': 'sample-a_R2.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
            'md5': 'md5-sample-a-r2',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA',
        },
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-b',
            'file_role': 'read1',
            'file_name': 'sample-b_R1.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
            'md5': 'md5-sample-b-r1',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA',
        },
        {
            'local_submission_alias': 'sub-2026-alpha',
            'local_sample_alias': 'sample-b',
            'file_role': 'read2',
            'file_name': 'sample-b_R2.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
            'md5': 'md5-sample-b-r2',
            'transfer_ticket': 'XFER-SUB-2026-ALPHA',
        },
    ]

    assert cast(dict[str, object], final_package['submission_metadata'].to_data()) == {
        'local_submission_alias': 'sub-2026-alpha',
        'local_sample_aliases': ['sample-b', 'sample-a'],
        'project_code': 'NORW-PATH-42',
        'study_title': 'Northern waterways genomic surveillance pilot',
        'release_date': '2026-06-15',
        'submission_checklist_version': 'ENA-CHECKLIST-1.0',
        'transfer_status': 'completed-external',
        'archive_status': 'submitted',
        'sequence_depot_submission_id': 'SEQDEPOT-SUB-2026-ALPHA',
        'external_transfer_ticket': 'XFER-SUB-2026-ALPHA',
        'final_receipt_message': 'Submitted submission sub-2026-alpha to Sequence Depot',
        'workflow_events': [
            'metadata_normalized',
            'storage_manifest_verified',
            'sequence_depot_submission_id_allocated',
            'external_transfer_completed',
            'biosamplevault_samples_registered',
            'sequence_depot_submission_finalized',
        ],
    }

    assert build_external_transfer_manifest(final_package) == {
        'local_submission_alias': 'sub-2026-alpha',
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

    assert build_sequence_depot_submission_id_request(final_package) == {
        'local_submission_alias': 'sub-2026-alpha',
        'project_code': 'NORW-PATH-42',
        'local_sample_aliases': ['sample-b', 'sample-a'],
    }
    assert build_biosamplevault_registration_request(final_package) == [
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
    assert build_sequence_depot_submission_payload(final_package) == \
        expected_sequence_depot_submission_payload()

    assert_job_state(brokering_flow, [RunState.FINISHED])


@TaskTemplate()
def normalize_submission_package(package: SubmissionPackage) -> SubmissionPackage:
    validate_submission_linkage(package)
    return append_workflow_event(clone_submission_package(package), 'metadata_normalized')


@TaskTemplate()
async def verify_storage_manifest(package: SubmissionPackage) -> SubmissionPackage:
    await asyncio.sleep(0)

    files = cast(list[dict[str, object]], package['submission_files'].to_data())
    assert all(cast(str, file_row['storage_uri']).startswith('s3://') for file_row in files)
    assert all(cast(str, file_row['md5']).startswith('md5-') for file_row in files)

    verified_package = update_submission_metadata(package, archive_status='files-verified')
    return append_workflow_event(verified_package, 'storage_manifest_verified')


@TaskTemplate()
async def allocate_sequence_depot_submission_id(package: SubmissionPackage) -> SubmissionPackage:
    await asyncio.sleep(0)

    request_payload = build_sequence_depot_submission_id_request(package)
    allocated_package = update_submission_metadata(
        package,
        sequence_depot_submission_id='SEQDEPOT-SUB-2026-ALPHA',
    )
    package_with_event = append_workflow_event(
        allocated_package,
        'sequence_depot_submission_id_allocated',
    )

    metadata = cast(dict[str, object], package_with_event['submission_metadata'].to_data())
    assert request_payload == {
        'local_submission_alias': metadata['local_submission_alias'],
        'project_code': metadata['project_code'],
        'local_sample_aliases': metadata['local_sample_aliases'],
    }

    return package_with_event


@TaskTemplate()
async def coordinate_external_transfer(package: SubmissionPackage) -> SubmissionPackage:
    await asyncio.sleep(0)

    transfer_manifest = build_external_transfer_manifest(package)
    assert transfer_manifest['local_submission_alias'] == 'sub-2026-alpha'

    updated_files = []
    for file_row in cast(list[dict[str, object]], package['submission_files'].to_data()):
        updated_files.append(file_row | {'transfer_ticket': 'XFER-SUB-2026-ALPHA'})

    transferred_package = update_submission_files(package, updated_files)
    transferred_package = update_submission_metadata(
        transferred_package,
        transfer_status='completed-external',
        external_transfer_ticket='XFER-SUB-2026-ALPHA',
    )
    return append_workflow_event(transferred_package, 'external_transfer_completed')


@TaskTemplate()
async def register_samples_with_biosamplevault(package: SubmissionPackage) -> SubmissionPackage:
    await asyncio.sleep(0)

    registration_request = build_biosamplevault_registration_request(package)
    updated_samples = []
    for sample in cast(list[dict[str, object]], package['submission_samples'].to_data()):
        sample_alias = cast(str, sample['local_sample_alias'])
        updated_samples.append(sample | {
            'biosamplevault_sample_id': f'BSV-{sample_alias.upper()}',
        })

    registered_package = update_submission_samples(package, updated_samples)
    registered_package = update_submission_metadata(
        registered_package,
        archive_status='samples-registered',
    )
    package_with_event = append_workflow_event(
        registered_package,
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

    return package_with_event


@TaskTemplate()
async def finalize_sequence_depot_submission(package: SubmissionPackage) -> SubmissionPackage:
    await asyncio.sleep(0)

    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    assert metadata['sequence_depot_submission_id'] == 'SEQDEPOT-SUB-2026-ALPHA'
    assert metadata['transfer_status'] == 'completed-external'

    final_payload = build_sequence_depot_submission_payload(package)
    assert final_payload == expected_sequence_depot_submission_payload()

    submitted_package = update_submission_metadata(
        package,
        archive_status='submitted',
        final_receipt_message='Submitted submission sub-2026-alpha to Sequence Depot',
    )
    submitted_package = append_workflow_event(
        submitted_package,
        'sequence_depot_submission_finalized',
    )
    assert_submission_ready_for_final_submission(submitted_package)
    return submitted_package


@FuncFlowTemplate()
async def broker_sequence_submission_flow(package: SubmissionPackage) -> SubmissionPackage:
    normalized_package = normalize_submission_package(package)
    verified_package = await verify_storage_manifest(normalized_package)
    package_with_submission_id = await allocate_sequence_depot_submission_id(verified_package)
    transferred_package = await coordinate_external_transfer(package_with_submission_id)
    sample_registered_package = await register_samples_with_biosamplevault(transferred_package)
    return await finalize_sequence_depot_submission(sample_registered_package)
