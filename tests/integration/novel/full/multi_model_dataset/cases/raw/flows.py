from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.multi import MultiModelDataset

from ...helpers.models import GeneralTable, RecordSchemaDef
from .tasks import apply_models_to_dataset, extract_record_schema_def


@DagFlowTemplate(
    extract_record_schema_def.refine(
        param_key_map={'dataset': 'tables'},
        result_key='record_schema_defs',
        iterate_over_data_files=True,
    ),
    apply_models_to_dataset.refine(param_key_map={'dataset': 'tables'}),
    consume_kwargs_from_results=False,
    name='specialize_record_models',
)
def specialize_record_models_dag_flow(  # type: ignore
        tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:  # noqa
    """Return specialize record models dag flow."""
    ...


@FuncFlowTemplate(name='specialize_record_models')
def specialize_record_models_func_flow(
        tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:
    """Return specialize record models func flow."""
    record_schema_defs = Dataset[RecordSchemaDef]([
        (table_name, extract_record_schema_def(table)) for table_name, table in tables.items()
    ])
    return apply_models_to_dataset(tables, record_schema_defs)
