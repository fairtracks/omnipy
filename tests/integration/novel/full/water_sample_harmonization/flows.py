from omnipy.components.general.tasks import (
    concat_all_vals_in_datasets_as_args,
    create_dataset_from_args,
    union_all_datasets_as_kwargs,
)
from omnipy.components.json.flows import flatten_nested_json
from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.compute.flow import DagFlowTemplate, LinearFlowTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsDataset

from .models import (NormalizedRiverSampleRecordMapper,
                     NormalizedSamplesDataset,
                     NormalizedWastewaterSampleRecordMapper)
from .tasks import create_sample_and_measurements_tables, fetch_sample_pages


@LinearFlowTemplate(
    fetch_sample_pages,  # takes: sample_page_urls
    concat_all_vals_in_datasets_as_args,
    create_dataset_from_args.refine(
        param_key_map=dict(
            dataset_cls='mapper_dataset_cls',
            key='concat_pages_key',
        )
    ),
    NormalizedSamplesDataset,
)
async def collect_and_normalize_samples(
    *,
    sample_page_urls: HttpUrlDataset,
    mapper_dataset_cls: type[IsDataset],
    concat_pages_key: str,
) -> NormalizedSamplesDataset: ...


@DagFlowTemplate(
    collect_and_normalize_samples.refine(
        name='collect_and_normalize_river_samples',
        param_key_map=dict(sample_page_urls='river_urls'),
        fixed_params=dict(
            mapper_dataset_cls=Dataset[Model[list[NormalizedRiverSampleRecordMapper]]],
            concat_pages_key='all_river_samples',
        ),
    ),
    collect_and_normalize_samples.refine(
        name='collect_and_normalize_wastewater_samples',
        param_key_map=dict(sample_page_urls='wastewater_urls'),
        fixed_params=dict(
            mapper_dataset_cls=Dataset[Model[list[NormalizedWastewaterSampleRecordMapper]]],
            concat_pages_key='all_wastewater_samples',
        ),
    ),
    union_all_datasets_as_kwargs,
)
async def env_monitoring_harmonization_flow(
    *,
    river_urls: HttpUrlDataset,
    wastewater_urls: HttpUrlDataset,
) -> NormalizedSamplesDataset: ...


@LinearFlowTemplate(
    concat_all_vals_in_datasets_as_args,
    create_dataset_from_args.refine(
        fixed_params=dict(
            dataset_cls=NormalizedSamplesDataset,
            key='all_normalized_samples',
        )
    ),
    flatten_nested_json,
    PandasDataset,
    create_sample_and_measurements_tables,
)
def flatten_and_wrangle_as_dataframe(
    samples_dataset: 'NormalizedSamplesDataset',
) -> PandasDataset: ...
