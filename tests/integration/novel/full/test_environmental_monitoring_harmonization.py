import asyncio
from collections.abc import Iterable
from inspect import isawaitable
from typing import Annotated, Any, cast

from aiohttp.test_utils import TestServer
import pytest

from omnipy import (Dataset,
                    FuncFlowTemplate,
                    HttpUrlDataset,
                    HttpUrlModel,
                    JsonListOfDictsDataset,
                    PandasDataset,
                    TaskTemplate)
from omnipy.components.json.flows import flatten_nested_json
from omnipy.shared.enums.job import RunState

from ....engine.helpers.functions import assert_job_state

pytest_plugins = ['tests.integration.novel.full.helpers.monitoring_services']


class MonitoringTables(Dataset[PandasDataset]):
    ...


def _table_records(table_dataset: PandasDataset, table_name: str) -> list[dict[str, object]]:
    records = cast(Any, table_dataset[table_name].content).to_dict(orient='records')
    return cast(list[dict[str, object]], records)


def _service_base_url(service: TestServer, source_name: str) -> str:
    port = service.make_url('/').port
    assert port is not None
    return f'http://localhost:{port}/{source_name}'


def _selected_columns(records: list[dict[str, object]], *column_names:
                      str) -> list[dict[str, object]]:
    selected_rows = []
    for record in records:
        selected_rows.append({column_name: record[column_name] for column_name in column_names})
    return selected_rows


def _page_number(page_key: str) -> int:
    return int(page_key.rsplit('_', 1)[1])


def _flatten_pages(batch_dataset: JsonListOfDictsDataset) -> list[dict[str, object]]:
    batch_data = batch_dataset.to_data()
    flattened_records: list[dict[str, object]] = []

    for page_key in sorted(batch_data, key=_page_number):
        flattened_records.extend(cast(list[dict[str, object]], batch_data[page_key]))

    return flattened_records


def _shared_backbone(catchment_id: str, monitoring_date: str) -> str:
    return f'{catchment_id}@{monitoring_date}'


def _normalize_river_measurements(
        measurements: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    normalized_measurements: list[dict[str, object]] = []

    for measurement in measurements:
        if 'value_mg_l' in measurement:
            normalized_measurements.append({
                'analyte': measurement['name'],
                'value_mg_l': measurement['value_mg_l'],
                'unit': 'mg/L',
            })
        elif 'value_ug_l' in measurement:
            normalized_measurements.append({
                'analyte': measurement['name'],
                'value_mg_l': cast(float, measurement['value_ug_l']) / 1000,
                'unit': 'mg/L',
            })
        else:
            normalized_measurements.append({
                'analyte': measurement['name'],
                'value_mg_l': measurement['value_celsius'],
                'unit': 'degC',
            })

    return normalized_measurements


def _normalize_wastewater_measurements(  # noqa: E125
        measurements: Iterable[dict[str, object]],) -> list[dict[str, object]]:
    return [{
        'analyte': measurement['metric'],
        'value_mg_l': float(cast(str, measurement['value'])),
        'unit': measurement['unit'],
    } for measurement in measurements]


def _normalize_source_batches(
    source_type: str,
    source_order: int,
    raw_records: list[dict[str, object]],
) -> list[dict[str, object]]:
    normalized_batches: list[dict[str, object]] = []

    for raw_record in raw_records:
        if source_type == 'river':
            catchment_id = cast(str, raw_record['catchment'])
            monitoring_date = cast(str, raw_record['sampled_at'])
            normalized_measurements = _normalize_river_measurements(
                cast(Iterable[dict[str, object]], raw_record['measurements']))
            location_name = raw_record['station']
        else:
            catchment_id = cast(str, raw_record['catchment_code'])
            monitoring_date = cast(str, raw_record['monitoring_date'])
            normalized_measurements = _normalize_wastewater_measurements(
                cast(Iterable[dict[str, object]], raw_record['measurements']))
            location_name = raw_record['treatment_plant']

        normalized_batches.append({
            'source_type': source_type,
            'source_order': source_order,
            'sample_key': cast(str, raw_record['sample_alias']).lower(),
            'catchment_id': catchment_id,
            'monitoring_date': monitoring_date,
            'location_name': location_name,
            'shared_backbone': _shared_backbone(catchment_id, monitoring_date),
            'measurements': normalized_measurements,
        })

    return normalized_batches


def _sort_parent_rows(parent_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        parent_rows,
        key=lambda row: (
            cast(str, row['monitoring_date']),
            cast(int, row['source_order']),
            cast(str, row['sample_key']),),
    )


def _sort_measurement_rows(measurement_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        measurement_rows,
        key=lambda row: (
            cast(str, row['monitoring_date']),
            cast(int, row['source_order']),
            cast(str, row['sample_key']),
            cast(str, row['_omnipy_id']),),
    )


def build_paginated_source_urls(source_name: str, port: int | None, endpoint: str,
                                page_count: int) -> HttpUrlDataset:
    urls = HttpUrlDataset()

    for page in range(page_count):
        url = HttpUrlModel('http://localhost')
        url.port = port
        url.path /= endpoint
        url.query['page'] = page
        urls[f'{source_name}_page_{page}'] = url

    return urls


async def test_environmental_monitoring_harmonization(
    runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
    river_service: Annotated[TestServer, pytest.fixture],
    wastewater_service: Annotated[TestServer, pytest.fixture],
) -> None:
    river_urls = build_paginated_source_urls(
        'river',
        river_service.port,
        'samples',
        page_count=2,
    )
    wastewater_urls = build_paginated_source_urls(
        'wastewater',
        wastewater_service.port,
        'retrieve_samples',
        page_count=2,
    )

    monitoring_flow = environmental_monitoring_harmonization_flow.apply()
    harmonized_tables_result = monitoring_flow(river_urls, wastewater_urls)
    harmonized_tables = await harmonized_tables_result \
        if isawaitable(harmonized_tables_result) else harmonized_tables_result

    assert set(harmonized_tables.keys()) == {'samples', 'measurements'}

    sample_records = _selected_columns(
        _table_records(harmonized_tables['samples'], 'samples'),
        'source_type',
        'sample_key',
        'catchment_id',
        'monitoring_date',
        'location_name',
        'shared_backbone',
    )
    measurement_records = _selected_columns(
        _table_records(harmonized_tables['measurements'], 'measurements'),
        'sample_key',
        'catchment_id',
        'monitoring_date',
        'analyte',
        'value_mg_l',
        'unit',
    )

    assert sample_records == [
        {
            'source_type': 'river',
            'sample_key': 'river-r1',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-03',
            'location_name': 'River Mouth',
            'shared_backbone': 'glomma-upper@2026-05-03',
        },
        {
            'source_type': 'wastewater',
            'sample_key': 'ww-9a',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-03',
            'location_name': 'North Works',
            'shared_backbone': 'glomma-upper@2026-05-03',
        },
        {
            'source_type': 'river',
            'sample_key': 'river-r2',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-10',
            'location_name': 'River Mouth',
            'shared_backbone': 'glomma-upper@2026-05-10',
        },
        {
            'source_type': 'wastewater',
            'sample_key': 'ww-9b',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-10',
            'location_name': 'North Works',
            'shared_backbone': 'glomma-upper@2026-05-10',
        },
        {
            'source_type': 'river',
            'sample_key': 'river-r3',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-17',
            'location_name': 'Upstream Bend',
            'shared_backbone': 'glomma-upper@2026-05-17',
        },
    ]

    assert measurement_records == [
        {
            'sample_key': 'river-r1',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-03',
            'analyte': 'nitrate',
            'value_mg_l': 1.2,
            'unit': 'mg/L',
        },
        {
            'sample_key': 'river-r1',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-03',
            'analyte': 'phosphorus',
            'value_mg_l': 0.12,
            'unit': 'mg/L',
        },
        {
            'sample_key': 'ww-9a',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-03',
            'analyte': 'ammonium',
            'value_mg_l': 0.8,
            'unit': 'mg/L',
        },
        {
            'sample_key': 'ww-9a',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-03',
            'analyte': 'phosphorus',
            'value_mg_l': 0.15,
            'unit': 'mg/L',
        },
        {
            'sample_key': 'river-r2',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-10',
            'analyte': 'nitrate',
            'value_mg_l': 1.4,
            'unit': 'mg/L',
        },
        {
            'sample_key': 'ww-9b',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-10',
            'analyte': 'ammonium',
            'value_mg_l': 0.75,
            'unit': 'mg/L',
        },
        {
            'sample_key': 'river-r3',
            'catchment_id': 'glomma-upper',
            'monitoring_date': '2026-05-17',
            'analyte': 'temperature',
            'value_mg_l': 9.8,
            'unit': 'degC',
        },
    ]

    assert_job_state(monitoring_flow, [RunState.FINISHED])


@TaskTemplate()
async def collect_river_batches(river_urls: HttpUrlDataset) -> JsonListOfDictsDataset:
    loaded_batches = JsonListOfDictsDataset.load(river_urls, as_mime_type='application/json')
    return await loaded_batches if isinstance(loaded_batches, asyncio.Task) else loaded_batches


@TaskTemplate()
async def collect_wastewater_batches(wastewater_urls: HttpUrlDataset) -> JsonListOfDictsDataset:
    loaded_batches = JsonListOfDictsDataset.load(wastewater_urls, as_mime_type='application/json')
    return await loaded_batches if isinstance(loaded_batches, asyncio.Task) else loaded_batches


@FuncFlowTemplate()
def harmonize_monitoring_batches(
    river_batches: JsonListOfDictsDataset,
    wastewater_batches: JsonListOfDictsDataset,
) -> MonitoringTables:
    normalized_batches = _normalize_source_batches('river', 0, _flatten_pages(river_batches))
    normalized_batches.extend(
        _normalize_source_batches('wastewater', 1, _flatten_pages(wastewater_batches)))

    flattened_batches = flatten_nested_json.run(  # type: ignore[call-arg]
        JsonListOfDictsDataset(measurements=normalized_batches))
    flattened_data = flattened_batches.to_data()

    parent_rows = cast(list[dict[str, object]], flattened_data['measurements'])
    sorted_parent_rows = _sort_parent_rows(parent_rows)
    parent_rows_by_id = {cast(str, row['_omnipy_id']): row for row in sorted_parent_rows}

    sample_rows = [{
        'source_type': row['source_type'],
        'sample_key': row['sample_key'],
        'catchment_id': row['catchment_id'],
        'monitoring_date': row['monitoring_date'],
        'location_name': row['location_name'],
        'shared_backbone': row['shared_backbone'],
    } for row in sorted_parent_rows]

    flattened_measurements = cast(list[dict[str, object]],
                                  flattened_data['measurements.measurements'])
    enriched_measurements = []

    for measurement in flattened_measurements:
        parent_row = parent_rows_by_id[cast(str, measurement['_omnipy_ref'])]
        enriched_measurements.append({
            '_omnipy_id': measurement['_omnipy_id'],
            'source_order': parent_row['source_order'],
            'sample_key': parent_row['sample_key'],
            'catchment_id': parent_row['catchment_id'],
            'monitoring_date': parent_row['monitoring_date'],
            'analyte': measurement['analyte'],
            'value_mg_l': measurement['value_mg_l'],
            'unit': measurement['unit'],
        })

    measurement_rows = [{
        'sample_key': row['sample_key'],
        'catchment_id': row['catchment_id'],
        'monitoring_date': row['monitoring_date'],
        'analyte': row['analyte'],
        'value_mg_l': row['value_mg_l'],
        'unit': row['unit'],
    } for row in _sort_measurement_rows(enriched_measurements)]

    return MonitoringTables(
        samples=PandasDataset(samples=sample_rows),
        measurements=PandasDataset(measurements=measurement_rows),
    )


@FuncFlowTemplate()
async def environmental_monitoring_harmonization_flow(
    river_urls: HttpUrlDataset,
    wastewater_urls: HttpUrlDataset,
) -> MonitoringTables:
    river_batches, wastewater_batches = await asyncio.gather(
        collect_river_batches(river_urls),
        collect_wastewater_batches(wastewater_urls),
    )
    return harmonize_monitoring_batches(river_batches, wastewater_batches)
