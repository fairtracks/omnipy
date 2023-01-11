from unifair.compute.flow import DagFlowTemplate, FuncFlowTemplate
from unifair.data.dataset import Dataset, MultiModelDataset

from ...helpers.models import GeneralTable, RecordSchemaDef
from .tasks import (apply_models_to_dataset,
                    extract_record_schema_def,
                    merge_key_value_into_str,
                    square_root,
                    uppercase)


@DagFlowTemplate(
    uppercase.refine(result_key='upper'),
    square_root,
    merge_key_value_into_str.refine(param_key_map={
        'key': 'upper',
        'val': 'pos_root',
    }),
    name='pos_square_root',
    result_key='pos_square_root')
def pos_square_root_dag_flow(
        number: int,  # noqa
        text: str,  # noqa
) -> str:
    ...


@FuncFlowTemplate(name='pos_square_root', result_key='pos_square_root')
def pos_square_root_func_flow(
    number: int,
    text: str,
) -> str:
    upper = uppercase(text)
    _neg_root, pos_root = square_root(number).values()
    return merge_key_value_into_str(upper, pos_root)


@DagFlowTemplate(
    extract_record_schema_def.refine(
        param_key_map={'dataset': 'tables'},
        result_key='record_schema_defs',
        iterate_over_data_files=True,
    ),
    apply_models_to_dataset.refine(param_key_map={'dataset': 'tables'}),
    name='specialize_record_models',
)
def specialize_record_models_dag_flow(
        tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:  # noqa
    ...


@FuncFlowTemplate(name='specialize_record_models')
def specialize_record_models_func_flow(
        tables: Dataset[GeneralTable]) -> MultiModelDataset[GeneralTable]:
    record_schema_defs = Dataset[RecordSchemaDef]([
        (table_name, extract_record_schema_def(table)) for table_name, table in tables.items()
    ])
    return apply_models_to_dataset(tables, record_schema_defs)
