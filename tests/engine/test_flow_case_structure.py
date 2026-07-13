from pathlib import Path

import ast


def test_flow_cases_define_no_local_task_templates() -> None:
    flows_module = Path(__file__).parent / 'cases' / 'flows.py'

    assert '@TaskTemplate()' not in flows_module.read_text()


def test_all_exported_raw_tasks_are_used_in_flow_cases() -> None:
    cases_dir = Path(__file__).parent / 'cases'
    flows_source = (cases_dir / 'flows.py').read_text()
    raw_tasks_source = (cases_dir / 'raw' / 'tasks.py').read_text()

    raw_tasks_module = ast.parse(raw_tasks_source)
    task_names = [
        node.name for node in raw_tasks_module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    for task_name in task_names:
        assert flows_source.count(task_name) > 1, task_name


def test_raw_task_catalog_omits_redundant_wrapper_exports() -> None:
    raw_tasks_source = (Path(__file__).parent / 'cases' / 'raw' / 'tasks.py').read_text()

    for redundant_task_name in (
        'add_three',
        'add_four',
        'add_five',
        'add_ten',
        'compute_mapped_input',
        'compute_mapped_multiplier',
        'compute_offset',
        'compute_async_value',
        'async_add_five',
        'async_add_ten',
        'emit_sync_series',
        'emit_offset_async_values',
        'generate_tripled_values',
        'finish_value',
        'multiply_number',
        'multiply_by_three',
        'multiply_by_four',
        'return_child_result',
        'subtract_one',
        'subtract_two',
        'subtract_three',
    ):
        assert f'def {redundant_task_name}(' not in raw_tasks_source
