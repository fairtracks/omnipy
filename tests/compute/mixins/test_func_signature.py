from inspect import Parameter

from omnipy.compute.task import TaskTemplate
import pytest
import pytest_cases as pc

from ..cases.raw.functions import format_to_string_func
from ..cases.tasks import TaskCase


@pc.parametrize_with_cases('case', cases='..cases.tasks')
def test_property_param_signature_and_return_type_task(case: TaskCase) -> None:

    task_template = TaskTemplate(case.task_func)

    for task_obj in task_template, task_template.apply():
        case.assert_signature_and_return_type_func(task_obj)


def test_property_param_signature_and_return_type_immutable_task() -> None:

    task_template = TaskTemplate(format_to_string_func)

    for task_obj in task_template, task_template.apply():
        with pytest.raises(AttributeError):
            task_obj.param_signatures = {}  # noqa

        with pytest.raises(TypeError):
            task_obj.param_signatures['new'] = Parameter(  # noqa
                'new', Parameter.POSITIONAL_OR_KEYWORD, annotation=bool)

        with pytest.raises(AttributeError):
            task_obj.return_type = int
