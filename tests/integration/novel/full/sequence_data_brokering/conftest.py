from collections.abc import Iterator
from itertools import count

import pytest

from .services import biosample_vault_sample_id_generator_context


@pytest.fixture(scope='function')
def samples() -> dict[str, dict[str, str]]:
    return {
        'Sample-A': {
            'local_sample_alias': 'Sample-A',
            'specimen_type': 'wastewater solids',
            'collection_site': 'North Works',
            'sampled_at': '2026-05-03',
        },
        'Sample-B': {
            'local_sample_alias': 'Sample-B',
            'specimen_type': 'river grab',
            'collection_site': 'River Mouth',
            'sampled_at': '2026-05-10',
        },
    }


@pytest.fixture(scope='function')
def files() -> dict[str, dict[str, str]]:
    return {
        'file-id-1': {
            'file_id': 'file-id-1',
            'local_sample_alias': 'Sample-A',
            'file_role': 'read1',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
            'md5': 'd2fc58de0e46e6a1a036bf323f7b501f',
        },
        'file-id-2': {
            'file_id': 'file-id-2',
            'local_sample_alias': 'Sample-A',
            'file_role': 'read2',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
            'md5': '61c4828d7d8e13f8872d1185b28ac492',
        },
        'file-id-3': {
            'file_id': 'file-id-3',
            'local_sample_alias': 'Sample-B',
            'file_role': 'read1',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
            'md5': '525821c178b6b23320fa56bfaa66e4e4',
        },
        'file-id-4': {
            'file_id': 'file-id-4',
            'local_sample_alias': 'Sample-B',
            'file_role': 'read2',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
            'md5': 'c0c488a07871ca1c742ce848ce905741',
        },
    }


@pytest.fixture(scope='function')
def metadata() -> dict[str, str | list[str]]:
    return {
        'broker_id': 'omnipy-broker',
        'project_code': 'NORW-PATH-42',
        'local_submission_alias': 'SUB-2026-ALPHA',
        'study_title': 'Northern waterways genomic surveillance pilot',
        'release_date': '2026-06-15',
        'submission_checklist_version': 'SQD-paired-reads-checklist-1.2',
    }


@pytest.fixture(scope='function')
def expected_sequence_depot_submission_payload() -> dict[str, object]:
    return {
        'files': {
            'file-id-1': {
                'file_id': 'file-id-1',
                'local_sample_alias': 'sample-a',
                'file_role': 'read1',
                'file_name': 'sample-a_R1.fastq.gz',
                'md5': 'd2fc58de0e46e6a1a036bf323f7b501f',
                'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
                'staging_storage_uri': 'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/'
                                       'sample-a_R1.fastq.gz',
                'transfer_status': 'completed',
                'error': None,
            },
            'file-id-2': {
                'file_id':
                    'file-id-2',
                'local_sample_alias':
                    'sample-a',
                'file_role':
                    'read2',
                'file_name':
                    'sample-a_R2.fastq.gz',
                'md5':
                    '61c4828d7d8e13f8872d1185b28ac492',
                'source_storage_uri':
                    's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
                'staging_storage_uri':
                    'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/sample-a_R2.fastq.gz',
                'transfer_status':
                    'completed',
                'error':
                    None,
            },
            'file-id-3': {
                'file_id':
                    'file-id-3',
                'local_sample_alias':
                    'sample-b',
                'file_role':
                    'read1',
                'file_name':
                    'sample-b_R1.fastq.gz',
                'md5':
                    '525821c178b6b23320fa56bfaa66e4e4',
                'source_storage_uri':
                    's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
                'staging_storage_uri':
                    'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/sample-b_R1.fastq.gz',
                'transfer_status':
                    'completed',
                'error':
                    None,
            },
            'file-id-4': {
                'file_id':
                    'file-id-4',
                'local_sample_alias':
                    'sample-b',
                'file_role':
                    'read2',
                'file_name':
                    'sample-b_R2.fastq.gz',
                'md5':
                    'c0c488a07871ca1c742ce848ce905741',
                'source_storage_uri':
                    's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
                'staging_storage_uri':
                    'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/sample-b_R2.fastq.gz',
                'transfer_status':
                    'completed',
                'error':
                    None,
            }
        },
        'metadata': {
            'broker_id': 'omnipy-broker',
            'local_submission_alias': 'sub-2026-alpha',
            'project_code': 'norw-path-42',
            'release_date': '2026-06-15',
            'sequence_depot_submission_id': 'SQD:4021372983',
            'study_title': 'Northern waterways genomic surveillance pilot',
            'submission_checklist_version': 'SQD-paired-reads-checklist-1.2',
        },
        'samples': {
            'Sample-A': {
                'biosample_vault_sample_id': 'BSV:80907461',
                'collection_site': 'North Works',
                'local_sample_alias': 'sample-a',
                'sampled_at': '2026-05-03',
                'specimen_type': 'wastewater solids'
            },
            'Sample-B': {
                'biosample_vault_sample_id': 'BSV:80907462',
                'collection_site': 'River Mouth',
                'local_sample_alias': 'sample-b',
                'sampled_at': '2026-05-10',
                'specimen_type': 'river grab'
            }
        },
        'status': {
            'biosample_vault_status': 'completed',
            'sequence_depot_submission_id_status': 'completed',
            'sequence_depot_submission_status': 'completed',
            'transfer_status': 'completed'
        }
    }


@pytest.fixture(scope='function')
def reset_biosample_vault_sample_id_generator() -> Iterator[None]:
    token = biosample_vault_sample_id_generator_context.set(count(start=80907461))
    yield
    biosample_vault_sample_id_generator_context.reset(token)
