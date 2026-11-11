import asyncio
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Annotated

from aiohttp import web
from aiohttp.test_utils import TestServer
import pytest
from pytest_aiohttp import AiohttpServer

from omnipy.components.remote.models import HttpUrlModel

JsonRequest = dict[str, object]

# Request bodies received by a mock service, per endpoint path
ReceivedRequests = dict[str, list[JsonRequest]]

Handler = Callable[[web.Request], Awaitable[web.Response]]

_received_requests_key = web.AppKey('received_requests', ReceivedRequests)


@pytest.fixture(scope='function')
def samples() -> dict[str, dict[str, str]]:
    return {
        'sample-a': {
            'local_sample_id': 'Sample-A',
            'specimen_type': 'wastewater solids',
            'collection_site': 'North Works',
            'sampled_at': '2026-05-03',
        },
        'sample-b': {
            'local_sample_id': 'Sample-B',
            'specimen_type': 'river grab',
            'collection_site': 'River Mouth',
            'sampled_at': '2026-05-10',
        },
    }


@pytest.fixture(scope='function')
def files() -> dict[str, dict[str, str]]:
    return {
        'file-id-1': {
            'local_file_id': 'file-id-1',
            'local_sample_id': 'Sample-A',
            'file_role': 'read1',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R1.fastq.gz',
            'md5': 'd2fc58de0e46e6a1a036bf323f7b501f',
        },
        'file-id-2': {
            'local_file_id': 'file-id-2',
            'local_sample_id': 'Sample-A',
            'file_role': 'read2',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
            'md5': '61c4828d7d8e13f8872d1185b28ac492',
        },
        'file-id-3': {
            'local_file_id': 'file-id-3',
            'local_sample_id': 'Sample-B',
            'file_role': 'read1',
            'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
            'md5': '525821c178b6b23320fa56bfaa66e4e4',
        },
        'file-id-4': {
            'local_file_id': 'file-id-4',
            'local_sample_id': 'Sample-B',
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
        'local_submission_id': 'SUB-2026-ALPHA',
        'study_title': 'Northern waterways genomic surveillance pilot',
        'release_date': '2026-06-15',
        'submission_checklist_version': 'SQD-paired-reads-checklist-1.2',
    }


@pytest.fixture(scope='function')
def expected_completed_submission(
    sequence_depot: Annotated['MockService', pytest.fixture],
    biosample_vault: Annotated['MockService', pytest.fixture],
    file_transfer: Annotated['MockService', pytest.fixture],
) -> dict[str, object]:
    return {
        'files': {
            'file-id-1': {
                'local_file_id': 'file-id-1',
                'local_sample_id': 'sample-a',
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
                'local_file_id': 'file-id-2',
                'local_sample_id': 'sample-a',
                'file_role': 'read2',
                'file_name': 'sample-a_R2.fastq.gz',
                'md5': '61c4828d7d8e13f8872d1185b28ac492',
                'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-a_R2.fastq.gz',
                'staging_storage_uri': 'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/sample-a_R2.fastq.gz',
                'transfer_status': 'completed',
                'error': None,
            },
            'file-id-3': {
                'local_file_id': 'file-id-3',
                'local_sample_id': 'sample-b',
                'file_role': 'read1',
                'file_name': 'sample-b_R1.fastq.gz',
                'md5': '525821c178b6b23320fa56bfaa66e4e4',
                'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R1.fastq.gz',
                'staging_storage_uri': 'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/sample-b_R1.fastq.gz',
                'transfer_status': 'completed',
                'error': None,
            },
            'file-id-4': {
                'local_file_id': 'file-id-4',
                'local_sample_id': 'sample-b',
                'file_role': 'read2',
                'file_name': 'sample-b_R2.fastq.gz',
                'md5': 'c0c488a07871ca1c742ce848ce905741',
                'source_storage_uri': 's3://lab-sequences/sub-2026-alpha/sample-b_R2.fastq.gz',
                'staging_storage_uri': 'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/sample-b_R2.fastq.gz',
                'transfer_status': 'completed',
                'error': None,
            },
        },
        'metadata': {
            'broker_id': 'omnipy-broker',
            'local_submission_id': 'sub-2026-alpha',
            'project_code': 'norw-path-42',
            'release_date': '2026-06-15',
            'sequence_depot_submission_id': 'SQD:4021372983',
            'study_title': 'Northern waterways genomic surveillance pilot',
            'submission_checklist_version': 'SQD-paired-reads-checklist-1.2',
        },
        'samples': {
            'sample-a': {
                'biosample_vault_sample_id': 'BSV:80907461',
                'collection_site': 'North Works',
                'local_sample_id': 'sample-a',
                'sampled_at': '2026-05-03',
                'specimen_type': 'wastewater solids',
            },
            'sample-b': {
                'biosample_vault_sample_id': 'BSV:80907462',
                'collection_site': 'River Mouth',
                'local_sample_id': 'sample-b',
                'sampled_at': '2026-05-10',
                'specimen_type': 'river grab',
            },
        },
        'logistics': {
            'services': {
                'sequence_depot': {'url': str(sequence_depot.url)},
                'biosample_vault': {'url': str(biosample_vault.url)},
                'file_transfer': {'url': str(file_transfer.url)},
            },
            'status': {
                'biosample_vault_status': 'completed',
                'sequence_depot_submission_id_status': 'completed',
                'sequence_depot_submission_status': 'completed',
                'transfer_status': 'completed',
            },
        },
    }


@pytest.fixture(scope='function')
def expected_sequence_depot_requests(
    expected_completed_submission: Annotated[dict[str, object], pytest.fixture],
) -> ReceivedRequests:
    final_submission = {
        key: value for key, value in expected_completed_submission.items() if key != 'logistics'
    }
    return {
        '/submission-ids': [
            {
                'local_submission_id': 'sub-2026-alpha',
                'project_code': 'norw-path-42',
                'sequence_depot_submission_id': None,
            },
        ],
        '/submissions': [final_submission],
    }


@pytest.fixture(scope='function')
def expected_biosample_vault_requests() -> ReceivedRequests:
    return {
        '/samples': [
            {
                'broker_id': 'omnipy-broker',
                'project_code': 'norw-path-42',
                'study_title': 'Northern waterways genomic surveillance pilot',
                'local_sample_id': 'sample-a',
                'specimen_type': 'wastewater solids',
                'geolocation': 'North Works',
                'sampling_date': '2026-05-03',
                'biosample_vault_sample_id': None,
            },
            {
                'broker_id': 'omnipy-broker',
                'project_code': 'norw-path-42',
                'study_title': 'Northern waterways genomic surveillance pilot',
                'local_sample_id': 'sample-b',
                'specimen_type': 'river grab',
                'geolocation': 'River Mouth',
                'sampling_date': '2026-05-10',
                'biosample_vault_sample_id': None,
            },
        ],
    }


@pytest.fixture(scope='function')
def expected_file_transfer_requests() -> ReceivedRequests:
    return {
        '/transfers': [
            {
                'username': 'omnipy-broker',
                'source_uri': f's3://lab-sequences/sub-2026-alpha/{file_name}',
                'target_uri': f'ftps://seq-depot-staging/omnipy-broker/sub-2026-alpha/{file_name}',
            }
            for file_name in (
                'sample-a_R1.fastq.gz',
                'sample-a_R2.fastq.gz',
                'sample-b_R1.fastq.gz',
                'sample-b_R2.fastq.gz',
            )
        ],
    }


# Mock HTTP endpoints simulating the external services. Each service records the request
# bodies it receives. Small response delays simulate service latency, keeping test run
# times low.


@web.middleware
async def _record_request(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    request.app[_received_requests_key].setdefault(request.path, []).append(await request.json())
    return await handler(request)


def _create_service_app(routes: Mapping[str, Handler]) -> web.Application:
    app = web.Application(middlewares=[_record_request])
    app[_received_requests_key] = {}
    for path, handler in routes.items():
        app.router.add_post(path, handler)
    return app


def _create_sequence_depot_app(
    submission_id: str,
    response_delay_secs: float,
) -> web.Application:
    async def _allocate_submission_id(request: web.Request) -> web.Response:
        submission_id_request = await request.json()
        await asyncio.sleep(response_delay_secs)
        return web.json_response(
            {**submission_id_request, 'sequence_depot_submission_id': submission_id}
        )

    async def _receive_submission(request: web.Request) -> web.Response:
        await asyncio.sleep(response_delay_secs)
        return web.json_response({'accepted': True})

    return _create_service_app(
        {
            '/submission-ids': _allocate_submission_id,
            '/submissions': _receive_submission,
        }
    )


def _create_biosample_vault_app(
    sample_ids: Mapping[str, str],
    response_delay_secs: float,
) -> web.Application:
    async def _register_sample(request: web.Request) -> web.Response:
        sample_submission = await request.json()
        sample_id = sample_ids[sample_submission['local_sample_id']]
        await asyncio.sleep(response_delay_secs)
        return web.json_response({**sample_submission, 'biosample_vault_sample_id': sample_id})

    return _create_service_app({'/samples': _register_sample})


def _create_file_transfer_app(response_delay_secs: float) -> web.Application:
    async def _transfer_file(request: web.Request) -> web.Response:
        await asyncio.sleep(response_delay_secs)
        return web.json_response({'status': 'completed', 'error': None})

    return _create_service_app({'/transfers': _transfer_file})


@dataclass(frozen=True)
class MockService:
    """A running mock service, with the request bodies it has received so far."""

    server: TestServer

    @property
    def url(self) -> HttpUrlModel:
        return HttpUrlModel(str(self.server.make_url('/')))

    @property
    def requests(self) -> ReceivedRequests:
        return self.server.app[_received_requests_key]


@pytest.fixture(scope='function')
async def sequence_depot(aiohttp_server: AiohttpServer) -> MockService:
    return MockService(
        await aiohttp_server(
            _create_sequence_depot_app(submission_id='SQD:4021372983', response_delay_secs=0.01)
        )
    )


@pytest.fixture(scope='function')
async def biosample_vault(aiohttp_server: AiohttpServer) -> MockService:
    return MockService(
        await aiohttp_server(
            _create_biosample_vault_app(
                sample_ids={'sample-a': 'BSV:80907461', 'sample-b': 'BSV:80907462'},
                response_delay_secs=0.01,
            )
        )
    )


@pytest.fixture(scope='function')
async def file_transfer(aiohttp_server: AiohttpServer) -> MockService:
    return MockService(await aiohttp_server(_create_file_transfer_app(response_delay_secs=0.05)))
