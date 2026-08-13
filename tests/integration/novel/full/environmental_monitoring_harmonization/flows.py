from omnipy.components.general.tasks import (concat_all_vals_in_datasets_as_args,
                                             create_dataset_from_args,
                                             union_all_datasets_as_kwargs)
from omnipy.components.json.flows import flatten_nested_json
from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.compute.flow import DagFlowTemplate, LinearFlowTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsDataset

from .models import (NormalizedBatchesDataset,
                     NormalizedRiverBatchRecordMapper,
                     NormalizedWastewaterBatchRecordMapper)
from .tasks import create_sample_and_measurements_tables, fetch_batches


@LinearFlowTemplate(
    fetch_batches,  # takes: batch_page_urls
    concat_all_vals_in_datasets_as_args,
    create_dataset_from_args.refine(
        param_key_map=dict(
            dataset_cls='mapper_dataset_cls',
            key='concat_pages_key',
        )),
    NormalizedBatchesDataset,
)
async def collect_and_normalize_batches(
    *,
    batch_page_urls: HttpUrlDataset,
    mapper_dataset_cls: type[IsDataset],
    concat_pages_key: str,
) -> NormalizedBatchesDataset:
    ...


@DagFlowTemplate(
    collect_and_normalize_batches.refine(
        name='collect_and_normalize_river_batches',
        param_key_map=dict(batch_page_urls='river_urls'),
        fixed_params=dict(
            mapper_dataset_cls=Dataset[Model[list[NormalizedRiverBatchRecordMapper]]],
            concat_pages_key='all_river_batches',
        ),
    ),
    collect_and_normalize_batches.refine(
        name='collect_and_normalize_wastewater_batches',
        param_key_map=dict(batch_page_urls='wastewater_urls'),
        fixed_params=dict(
            mapper_dataset_cls=Dataset[Model[list[NormalizedWastewaterBatchRecordMapper]]],
            concat_pages_key='all_wastewater_batches',
        ),
    ),
    union_all_datasets_as_kwargs,
)
async def env_monitoring_harmonization_flow(
    *,
    river_urls: HttpUrlDataset,
    wastewater_urls: HttpUrlDataset,
) -> NormalizedBatchesDataset:
    ...


@LinearFlowTemplate(
    concat_all_vals_in_datasets_as_args,
    create_dataset_from_args.refine(
        fixed_params=dict(
            dataset_cls=NormalizedBatchesDataset,
            key='all_normalized_batches',
        )),
    flatten_nested_json,
    PandasDataset,
    create_sample_and_measurements_tables,
)
def flatten_and_wrangle_as_dataframe(batches_dataset: 'NormalizedBatchesDataset') -> PandasDataset:
    ...
