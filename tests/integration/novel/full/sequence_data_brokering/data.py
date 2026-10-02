from .models import (SubmissionFilesDataset,
                     SubmissionMetadataModel,
                     SubmissionModel,
                     SubmissionSamplesDataset)


def build_sequence_submission() -> SubmissionModel:
    submission_samples = SubmissionSamplesDataset({
        'Sample-A': {
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_alias': 'Sample-A',
            'specimen_type': 'wastewater solids',
            'collection_site': 'North Works',
            'sampled_at': '2026-05-03',
        },
        'Sample-B': {
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_alias': 'Sample-B',
            'specimen_type': 'river grab',
            'collection_site': 'River Mouth',
            'sampled_at': '2026-05-10',
        },
    })
    submission_files = SubmissionFilesDataset({
        'file-id-1': {
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_alias': 'Sample-A',
            'file_id': 'file-id-1',
            'file_role': 'read1',
            'file_name': 'sample-a_R1.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
            'md5': 'md5-sample-a-r1',
        },
        'file-id-2': {
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_alias': 'Sample-A',
            'file_id': 'file-id-2',
            'file_role': 'read2',
            'file_name': 'sample-a_R2.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
            'md5': 'md5-sample-a-r2',
        },
        'file-id-3': {
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_alias': 'Sample-B',
            'file_id': 'file-id-3',
            'file_role': 'read1',
            'file_name': 'sample-b_R1.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
            'md5': 'md5-sample-b-r1',
        },
        'file-id-4': {
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_alias': 'Sample-B',
            'file_id': 'file-id-4',
            'file_role': 'read2',
            'file_name': 'sample-b_R2.fastq.gz',
            'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
            'md5': 'md5-sample-b-r2',
        },
    })
    submission_metadata = SubmissionMetadataModel({
        'local_submission_alias': 'SUB-2026-ALPHA',
        'local_sample_aliases': ['Sample-B', 'Sample-A'],
        'project_code': 'NORW-PATH-42',
        'study_title': 'Northern waterways genomic surveillance pilot',
        'release_date': '2026-06-15',
        'submission_checklist_version': 'ENA-CHECKLIST-1.0',
        'workflow_events': [],
    })

    return SubmissionModel(
        samples=submission_samples,
        files=submission_files,
        metadata=submission_metadata,
    )


def build_sequence_depot_submission_id_request(submission: SubmissionModel) -> dict[str, object]:
    return {
        'local_submission_alias': submission.metadata.local_submission_alias,
        'project_code': submission.metadata.project_code,
        'local_sample_aliases': submission.metadata.local_sample_aliases,
    }


def build_external_transfer_manifest(submission: SubmissionModel) -> dict[str, object]:
    return {
        'local_submission_alias':
            submission.metadata.local_submission_alias,
        'files': [{
            'local_sample_alias': file_row.local_sample_alias,
            'file_role': file_row.file_role,
            'file_name': file_row.file_name,
            'storage_uri': file_row.storage_uri,
            'md5': file_row.md5,
        } for file_row in submission.files.values()],
    }


def build_biosamplevault_registration_request(
        submission: SubmissionModel) -> list[dict[str, object]]:
    return [{
        'local_submission_alias': submission.metadata.local_submission_alias,
        'local_sample_alias': sample.local_sample_alias,
        'specimen_type': sample.specimen_type,
        'collection_site': sample.collection_site,
        'sampled_at': sample.sampled_at,
    } for sample in submission.samples.values()]


def expected_sequence_depot_submission_payload() -> dict[str, object]:
    return {
        'files': {
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
        },
        'metadata': {
            'archive_status':
                'submitted',
            'external_transfer_ticket':
                'XFER-SUB-2026-ALPHA',
            'final_receipt_message':
                'Submitted submission sub-2026-alpha to '
                'Sequence Depot',
            'local_sample_aliases': ['sample-b', 'sample-a'],
            'local_submission_alias':
                'sub-2026-alpha',
            'project_code':
                'NORW-PATH-42',
            'release_date':
                '2026-06-15',
            'sequence_depot_submission_id':
                'SEQDEPOT-SUB-2026-ALPHA',
            'study_title':
                'Northern waterways genomic surveillance pilot',
            'submission_checklist_version':
                'ENA-CHECKLIST-1.0',
            'transfer_status':
                'completed-external',
            'workflow_events': [
                'metadata_normalized',
                'storage_manifest_verified',
                'sequence_depot_submission_id_allocated',
                'external_transfer_completed',
                'biosamplevault_samples_registered',
                'sequence_depot_submission_finalized'
            ]
        },
        'samples': {
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
    }
