import asyncio

import pytest
import pytest_cases as pc

from omnipy.api.protocols.public.compute import IsTaskTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..cases.iterate_tasks import IterateDataFilesCase
from ..cases.raw.functions import data_import_func


def test_fail_property_iterate_over_data_files_no_arg_task() -> None:
    with pytest.raises(ValueError):
        TaskTemplate(iterate_over_data_files=True)(data_import_func)


@pc.parametrize_with_cases('case', cases='..cases.iterate_tasks')
def test_properties_default_values_task(case: IterateDataFilesCase) -> None:
    with pytest.raises(ValueError):
        TaskTemplate(iterate_over_data_files=None)(case.task_func)

    no_iter_default_template = TaskTemplate()(case.task_func)

    for task_obj in no_iter_default_template, no_iter_default_template.apply():
        assert task_obj.iterate_over_data_files is False
        assert task_obj.output_dataset_param is None
        assert task_obj.output_dataset_cls is None


@pc.parametrize_with_cases('case', cases='..cases.iterate_tasks')
def test_property_iterate_over_data_files_task(case: IterateDataFilesCase) -> None:
    iter_template = TaskTemplate(iterate_over_data_files=case.iterate_over_data_files)(
        case.task_func)

    for task_obj in (iter_template, iter_template.apply()):
        assert task_obj.iterate_over_data_files is case.iterate_over_data_files


@pc.parametrize_with_cases('case', cases='..cases.iterate_tasks')
def test_property_output_dataset_param_task(case: IterateDataFilesCase) -> None:
    iter_dataset_param_task_template_decorator = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_param='output_dataset',
    )

    if case.fail_with_output_dataset_param:
        with pytest.raises(ValueError):
            iter_dataset_param_task_template_decorator(case.task_func)
    else:
        iter_dataset_param_template = iter_dataset_param_task_template_decorator(case.task_func)

        for task_obj in (iter_dataset_param_template, iter_dataset_param_template.apply()):
            assert task_obj.output_dataset_param == 'output_dataset'


@pc.parametrize_with_cases('case', cases='..cases.iterate_tasks')
def test_property_output_dataset_cls_is_int_task(case: IterateDataFilesCase) -> None:
    iter_dataset_cls_template_decorator = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_cls=Dataset[Model[int]])

    if case.fail_with_output_dataset_cls_is_int:
        with pytest.raises(ValueError):
            iter_dataset_cls_template_decorator(case.task_func)
    else:
        iter_dataset_cls_template = iter_dataset_cls_template_decorator(case.task_func)

        for task_obj in (iter_dataset_cls_template, iter_dataset_cls_template.apply()):
            assert task_obj.output_dataset_cls is Dataset[Model[int]]


@pc.parametrize_with_cases('case', cases='..cases.iterate_tasks')
def test_property_output_dataset_param_and_cls_is_int_task(case: IterateDataFilesCase) -> None:
    iter_dataset_cls_task_template_decorator = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_param='output_dataset',
        output_dataset_cls=Dataset[Model[int]])

    if case.fail_with_output_dataset_param_and_cls_is_int:
        with pytest.raises(ValueError):
            iter_dataset_cls_task_template_decorator(case.task_func)
    else:
        iter_dataset_cls_template = iter_dataset_cls_task_template_decorator(case.task_func)

        for task_obj in (iter_dataset_cls_template, iter_dataset_cls_template.apply()):
            assert task_obj.output_dataset_cls is Dataset[Model[int]]


def _run_task_template(
    case: IterateDataFilesCase,
    task_template: IsTaskTemplate,
    dataset: Dataset[Model[int]],
    output_dataset: Dataset | None = None,
) -> Dataset[Model[str]] | asyncio.Task[Dataset[Model[str]]]:
    kwargs = case.kwargs
    if output_dataset is not None and case.iterate_over_data_files:
        kwargs['output_dataset'] = output_dataset
    return task_template.run(dataset, *case.args, **kwargs)


async def _ensure_dataset_await_if_task(case, dataset_or_task):
    if case.func_is_async:
        returned_dataset = await dataset_or_task
    else:
        returned_dataset = dataset_or_task
    return returned_dataset


@pc.parametrize_with_cases('case', cases='..cases.iterate_tasks', has_tag=['no_output_dataset'])
async def test_iterate_over_data_files_task(case: IterateDataFilesCase) -> None:

    task_template = TaskTemplate(iterate_over_data_files=case.iterate_over_data_files)(
        case.task_func)

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))

    dataset_or_task = _run_task_template(case, task_template, dataset)
    returned_dataset = await _ensure_dataset_await_if_task(case, dataset_or_task)

    assert returned_dataset.to_data() == dict(a='5', b='7', c='0')


@pc.parametrize_with_cases(
    'case', cases='..cases.iterate_tasks', has_tag=['iterate', 'str_output_dataset'])
async def test_iterate_over_data_files_with_output_dataset_param_task(
        case: IterateDataFilesCase) -> None:

    task_template = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_param='output_dataset')(
            case.task_func)

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))
    output_dataset = Dataset[Model[str]]()

    dataset_or_task = _run_task_template(case, task_template, dataset, output_dataset)
    returned_dataset = await _ensure_dataset_await_if_task(case, dataset_or_task)

    assert returned_dataset.to_data() == dict(a='5', b='7', c='0')


@pc.parametrize_with_cases(
    'case', cases='..cases.iterate_tasks', has_tag=['iterate', 'no_output_dataset'])
async def test_iterate_over_data_files_with_output_dataset_cls_is_int_task(
        case: IterateDataFilesCase) -> None:

    task_template = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_cls=Dataset[Model[int]])(
            case.task_func)

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))

    dataset_or_task = _run_task_template(case, task_template, dataset)
    returned_dataset = await _ensure_dataset_await_if_task(case, dataset_or_task)

    assert returned_dataset.to_data() == dict(a=5, b=7, c=0)


@pc.parametrize_with_cases(
    'case', cases='..cases.iterate_tasks', has_tag=['iterate', 'int_output_dataset'])
async def test_iterate_over_data_files_with_output_dataset_param_and_cls_is_int_task(
        case: IterateDataFilesCase) -> None:

    task_template = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_param='output_dataset',
        output_dataset_cls=Dataset[Model[int]])(
            case.task_func)

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))

    output_dataset = Dataset[Model[int]]()
    dataset_or_task = _run_task_template(case, task_template, dataset, output_dataset)
    returned_dataset = await _ensure_dataset_await_if_task(case, dataset_or_task)

    assert returned_dataset.to_data() == dict(a=5, b=7, c=0)


@pc.parametrize_with_cases(
    'case', cases='..cases.iterate_tasks', has_tag=['iterate', 'await_number_future'])
async def test_iterate_over_data_files_await_future_task(case: IterateDataFilesCase) -> None:

    task_template = TaskTemplate(
        iterate_over_data_files=case.iterate_over_data_files,
        output_dataset_param='output_dataset',
        output_dataset_cls=Dataset[Model[int]])(
            case.task_func)

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))

    output_dataset = Dataset[Model[int]]()
    dataset_or_task = _run_task_template(case, task_template, dataset, output_dataset)

    assert case.func_second_arg_is_future
    while len(output_dataset.pending_data) != 3:
        await asyncio.sleep(0.1)
    future_number = case.args[0]
    future_number.set_result(2)

    returned_dataset = await _ensure_dataset_await_if_task(case, dataset_or_task)

    assert returned_dataset.to_data() == dict(a=5, b=7, c=0)
