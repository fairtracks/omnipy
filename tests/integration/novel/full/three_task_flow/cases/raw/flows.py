from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate

from .tasks import merge_key_value_into_str, square_root, uppercase


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
