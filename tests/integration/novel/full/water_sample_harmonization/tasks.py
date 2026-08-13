from omnipy.components.json.datasets import JsonListOfDictsDataset
from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.pandas.tasks import join_tables
from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.compute.task import TaskTemplate
from omnipy.util.helpers import resolve


@TaskTemplate()
async def fetch_batches(*, batch_page_urls: HttpUrlDataset) -> JsonListOfDictsDataset:
    return await resolve(JsonListOfDictsDataset.load(batch_page_urls))


@TaskTemplate()
def create_sample_and_measurements_tables(dataset: PandasDataset) -> PandasDataset:
    out_dataset = PandasDataset()

    # Samples

    samples_cols_to_keep = ['sample_key', 'catchment_id', 'monitoring_date', 'location_name']
    out_dataset['samples'] = \
        dataset['all_normalized_batches'][samples_cols_to_keep]  # type: ignore[index]

    # Measurements

    measurements_df_model = join_tables(
        dataset['all_normalized_batches'],
        dataset['all_normalized_batches.measurements'],
        on_cols={'_omnipy_id': '_omnipy_ref'},
    )
    measurements_cols_to_keep = [
        'sample_key', 'monitoring_date', 'location_name', 'type', 'value', 'unit'
    ]
    measurements_df_model = measurements_df_model[measurements_cols_to_keep]  # type: ignore[index]
    measurements_df_model = measurements_df_model.sort_values(
        by=['monitoring_date', 'location_name'])
    out_dataset['measurements'] = measurements_df_model

    return out_dataset
