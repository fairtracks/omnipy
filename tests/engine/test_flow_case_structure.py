from pathlib import Path


def test_flow_cases_define_no_local_task_templates() -> None:
    flows_module = Path(__file__).parent / 'cases' / 'flows.py'

    assert '@TaskTemplate()' not in flows_module.read_text()
