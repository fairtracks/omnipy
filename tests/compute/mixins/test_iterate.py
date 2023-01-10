import pytest

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model

from ..cases.raw.functions import (all_data_files_plus_func,
                                   data_import_func,
                                   single_data_file_plus_func)


def test_property_iterate_over_data_files_default_task() -> None:

    all_plus_no_iter_template = TaskTemplate(all_data_files_plus_func)

    for all_plus_obj in all_plus_no_iter_template, all_plus_no_iter_template.apply():
        assert all_plus_obj.iterate_over_data_files is False

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))
    assert all_plus_no_iter_template.run(dataset, 2).to_data() == dict(a=5, b=7, c=0)

    with pytest.raises(TypeError):
        TaskTemplate(all_data_files_plus_func, iterate_over_data_files=None)

    all_plus_no_iter_template = TaskTemplate(
        all_data_files_plus_func, iterate_over_data_files=False)

    for all_plus_obj in all_plus_no_iter_template, all_plus_no_iter_template.apply():
        assert all_plus_obj.iterate_over_data_files is False


def test_property_iterate_over_data_files_true_task() -> None:

    all_plus_iter_template = TaskTemplate(single_data_file_plus_func, iterate_over_data_files=True)

    for all_plus_obj in all_plus_iter_template, all_plus_iter_template.apply():
        assert all_plus_obj.iterate_over_data_files is True

    dataset = Dataset[Model[int]](dict(a=3, b=5, c=-2))
    assert all_plus_iter_template.run(dataset, 2).to_data() == dict(a=5, b=7, c=0)


def test_fail_property_iterate_over_data_files_no_arg_task() -> None:
    with pytest.raises(AttributeError):
        TaskTemplate(data_import_func, iterate_over_data_files=True)
