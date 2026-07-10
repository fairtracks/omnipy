"""Flow definitions for integration novel full tests."""

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.multi import MultiModelDataset

from ...helpers.models import GeneralTable, RecordSchemaDef
from .tasks import (add_label,
                    apply_models_to_dataset,
                    extract_record_schema_def,
                    fetch_remote_value,
                    merge_key_value_into_str,
                    normalize_remote_value,
                    normalize_text,
                    square_root,
                    store_pipeline_result,
                    uppercase,
                    wrap_message)


@DagFlowTemplate(
    uppercase.refine(result_key='upper'),
    square_root,
    merge_key_value_into_str.refine(param_key_map={
        'key': 'upper',
        'val': 'pos_root',
    }),
    name='pos_square_root',
    result_key='pos_square_root')
def pos_square_root_dag_flow(  # type: ignore
        number: int,  # noqa
        text: str,  # noqa
) -> str:
    """Return pos square root dag flow."""
    ...


@FuncFlowTemplate(name='pos_square_root', result_key='pos_square_root')
def pos_square_root_func_flow(
    number: int,
    text: str,
) -> str:
    """Return pos square root func flow."""
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


@FuncFlowTemplate(name='async_io_pipeline')
async def async_io_pipeline_flow(seed: int) -> str:
    remote_value = await fetch_remote_value(seed)
    normalized_value = await normalize_remote_value(remote_value)
    return await store_pipeline_result(normalized_value, prefix='remote:')


@FuncFlowTemplate(name='label_formatter_child')
def label_formatter_child_flow(text: str, label: str) -> str:
    normalized = normalize_text(text)
    return add_label(normalized, label)


@DagFlowTemplate(
    label_formatter_child_flow.refine(
        fixed_params=dict(label='base-'),
        result_key='formatted',
    ),
    wrap_message.refine(param_key_map={'text': 'formatted'}),
    name='nested_subflow_composition',
    result_key='nested_subflow_composition',
)
def nested_subflow_composition_flow(text: str, left: str, right: str) -> str:
    ...


@FuncFlowTemplate(name='label_replacement_child')
def label_replacement_child_flow(text: str, label: str) -> str:
    normalized = normalize_text(text)
    return add_label(normalized, label)


@DagFlowTemplate(
    label_replacement_child_flow.refine(
        fixed_params=dict(label='base-'),
        result_key='formatted',
    ),
    wrap_message.refine(param_key_map={'text': 'formatted'}),
    name='subflow_replacement',
    result_key='subflow_replacement',
)
def subflow_replacement_flow(text: str, left: str, right: str) -> str:
    ...
