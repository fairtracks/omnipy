from typing import cast

from .submission_models import build_submission_package, SubmissionPackage


def build_sequence_submission_package() -> SubmissionPackage:
    return build_submission_package(
        submission_samples=[
            {
                'local_submission_alias': 'SUB-2026-ALPHA',
                'local_sample_alias': 'Sample-A',
                'specimen_type': 'wastewater solids',
                'collection_site': 'North Works',
                'sampled_at': '2026-05-03',
            },
            {
                'local_submission_alias': 'SUB-2026-ALPHA',
                'local_sample_alias': 'Sample-B',
                'specimen_type': 'river grab',
                'collection_site': 'River Mouth',
                'sampled_at': '2026-05-10',
            },
        ],
        submission_files=[
            {
                'local_submission_alias': 'SUB-2026-ALPHA',
                'local_sample_alias': 'Sample-A',
                'file_role': 'read1',
                'file_name': 'sample-a_R1.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
                'md5': 'md5-sample-a-r1',
            },
            {
                'local_submission_alias': 'SUB-2026-ALPHA',
                'local_sample_alias': 'Sample-A',
                'file_role': 'read2',
                'file_name': 'sample-a_R2.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
                'md5': 'md5-sample-a-r2',
            },
            {
                'local_submission_alias': 'SUB-2026-ALPHA',
                'local_sample_alias': 'Sample-B',
                'file_role': 'read1',
                'file_name': 'sample-b_R1.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
                'md5': 'md5-sample-b-r1',
            },
            {
                'local_submission_alias': 'SUB-2026-ALPHA',
                'local_sample_alias': 'Sample-B',
                'file_role': 'read2',
                'file_name': 'sample-b_R2.fastq.gz',
                'storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
                'md5': 'md5-sample-b-r2',
            },
        ],
        submission_metadata={
            'local_submission_alias': 'SUB-2026-ALPHA',
            'local_sample_aliases': ['Sample-B', 'Sample-A'],
            'project_code': 'NORW-PATH-42',
            'study_title': 'Northern waterways genomic surveillance pilot',
            'release_date': '2026-06-15',
            'submission_checklist_version': 'ENA-CHECKLIST-1.0',
            'workflow_events': [],
        },
    )


def build_sequence_depot_submission_id_request(package: SubmissionPackage) -> dict[str, object]:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    return {
        'local_submission_alias': metadata['local_submission_alias'],
        'project_code': metadata['project_code'],
        'local_sample_aliases': metadata['local_sample_aliases'],
    }


def build_external_transfer_manifest(package: SubmissionPackage) -> dict[str, object]:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    files = cast(list[dict[str, object]], package['submission_files'].to_data())
    return {
        'local_submission_alias':
            metadata['local_submission_alias'],
        'files': [{
            'local_sample_alias': file_row['local_sample_alias'],
            'file_role': file_row['file_role'],
            'file_name': file_row['file_name'],
            'storage_uri': file_row['storage_uri'],
            'md5': file_row['md5'],
        } for file_row in files],
    }


def build_biosamplevault_registration_request(
        package: SubmissionPackage) -> list[dict[str, object]]:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    samples = cast(list[dict[str, object]], package['submission_samples'].to_data())
    return [{
        'local_submission_alias': metadata['local_submission_alias'],
        'local_sample_alias': sample['local_sample_alias'],
        'specimen_type': sample['specimen_type'],
        'collection_site': sample['collection_site'],
        'sampled_at': sample['sampled_at'],
    } for sample in samples]


def build_sequence_depot_submission_payload(package: SubmissionPackage) -> dict[str, object]:
    metadata = cast(dict[str, object], package['submission_metadata'].to_data())
    samples = cast(list[dict[str, object]], package['submission_samples'].to_data())
    files = cast(list[dict[str, object]], package['submission_files'].to_data())
    return {
        'local_submission_alias':
            metadata['local_submission_alias'],
        'sequence_depot_submission_id':
            metadata['sequence_depot_submission_id'],
        'project_code':
            metadata['project_code'],
        'release_date':
            metadata['release_date'],
        'submission_checklist_version':
            metadata['submission_checklist_version'],
        'samples': [{
            'local_sample_alias': sample['local_sample_alias'],
            'biosamplevault_sample_id': sample['biosamplevault_sample_id'],
        } for sample in samples],
        'files': [{
            'local_sample_alias': file_row['local_sample_alias'],
            'file_role': file_row['file_role'],
            'transfer_ticket': file_row['transfer_ticket'],
            'file_name': file_row['file_name'],
        } for file_row in files],
    }


def expected_sequence_depot_submission_payload() -> dict[str, object]:
    return {
        'local_submission_alias':
            'sub-2026-alpha',
        'sequence_depot_submission_id':
            'SEQDEPOT-SUB-2026-ALPHA',
        'project_code':
            'NORW-PATH-42',
        'release_date':
            '2026-06-15',
        'submission_checklist_version':
            'ENA-CHECKLIST-1.0',
        'samples': [
            {
                'local_sample_alias': 'sample-a',
                'biosamplevault_sample_id': 'BSV-SAMPLE-A',
            },
            {
                'local_sample_alias': 'sample-b',
                'biosamplevault_sample_id': 'BSV-SAMPLE-B',
            },
        ],
        'files': [
            {
                'local_sample_alias': 'sample-a',
                'file_role': 'read1',
                'transfer_ticket': 'XFER-SUB-2026-ALPHA',
                'file_name': 'sample-a_R1.fastq.gz',
            },
            {
                'local_sample_alias': 'sample-a',
                'file_role': 'read2',
                'transfer_ticket': 'XFER-SUB-2026-ALPHA',
                'file_name': 'sample-a_R2.fastq.gz',
            },
            {
                'local_sample_alias': 'sample-b',
                'file_role': 'read1',
                'transfer_ticket': 'XFER-SUB-2026-ALPHA',
                'file_name': 'sample-b_R1.fastq.gz',
            },
            {
                'local_sample_alias': 'sample-b',
                'file_role': 'read2',
                'transfer_ticket': 'XFER-SUB-2026-ALPHA',
                'file_name': 'sample-b_R2.fastq.gz',
            },
        ],
    }
