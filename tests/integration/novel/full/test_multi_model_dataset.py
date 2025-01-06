import inspect
from inspect import Parameter
import os
from typing import Annotated

import pytest
import pytest_cases as pc

from omnipy.data.dataset import Dataset, MultiModelDataset
from omnipy.shared.enums import RunState
from omnipy.util.pydantic import ValidationError

from ....engine.helpers.functions import assert_job_state
from .cases.flows import FlowCase
from .helpers.models import GeneralTable, MyOtherRecordSchema, MyRecordSchema, TableTemplate


# TODO: After Pydantic v2 support: Add "-> None" to all tests to open up for mypy syntax checking
def test_table_models(runtime: Annotated[None, pytest.fixture]) -> None:
    GeneralTable([{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}])

    TableTemplate[MyRecordSchema]([{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}])

    with pytest.raises(ValidationError):
        TableTemplate[MyOtherRecordSchema]([{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}])


def test_dataset_with_multiple_table_models(runtime: Annotated[None, pytest.fixture]) -> None:
    my_dataset = MultiModelDataset[GeneralTable]()

    my_dataset['a'] = [{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}]
    assert my_dataset.get_model('a') == GeneralTable

    my_dataset.set_model('a', TableTemplate[MyRecordSchema])
    assert my_dataset.get_model('a') == TableTemplate[MyRecordSchema]

    my_dataset['b'] = [{'b': 'df', 'c': True}, {'b': 'sg', 'c': False}]
    with pytest.raises(ValidationError):
        my_dataset.set_model('b', TableTemplate[MyRecordSchema])
    assert my_dataset.get_model('b') == GeneralTable
    assert my_dataset['b'].to_data() == [{'b': 'df', 'c': True}, {'b': 'sg', 'c': False}]

    my_dataset.set_model('b', TableTemplate[MyOtherRecordSchema])
    assert my_dataset.get_model('b') == TableTemplate[MyOtherRecordSchema]
    assert my_dataset['b'].to_data() == [{'b': 'df', 'c': 1}, {'b': 'sg', 'c': 0}]

    my_dataset.set_model('c', TableTemplate[MyOtherRecordSchema])
    assert my_dataset.get_model('c') == TableTemplate[MyOtherRecordSchema]
    assert my_dataset['c'].contents == []

    with pytest.raises(ValidationError):
        my_dataset['c'] = [{'b': 'sd', 'd': False}, {'b': 'dd', 'd': False}]
    assert my_dataset['c'].contents == []
    my_dataset['c'] = [{'b': 'sd', 'c': False}, {'b': 'dd', 'c': False}]
    assert my_dataset['c'].to_data() == [{'b': 'sd', 'c': 0}, {'b': 'dd', 'c': 0}]

    del my_dataset['b']
    assert my_dataset.get_model('b') == TableTemplate[MyOtherRecordSchema]

    with pytest.raises(ValidationError):
        my_dataset.from_data({'c': [{'b': 'rt', 'd': True}, {'b': 'vf', 'd': True}]}, update=False)
    my_dataset.from_data({'c': [{'b': 'rt', 'c': True}, {'b': 'vf', 'c': True}]}, update=False)
    assert my_dataset.get_model('a') == TableTemplate[MyRecordSchema]

    with pytest.raises(ValidationError):
        my_dataset.update({'a': [{'a': 444, 'd': True}]})
    my_dataset.update({'a': [{'a': 444, 'b': 'fae'}]})
    assert my_dataset.get_model('a') == TableTemplate[MyRecordSchema]


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
TODO: Requires refactoring of Dataset class to use member variables instead of 'data' dict to
store objects. Idea: Add a '_data' private member with 'data' as alias to keep UserDict working,
however with no values to not duplicate content. Keep difference between Dataset and
MultiModelDataset as having two classes is useful for task typing, see e.g. the function
definition of 'specialize_record_models' below.
""")
def test_dataset_with_multiple_table_models_json_schema():
    my_dataset = MultiModelDataset[GeneralTable]()

    my_dataset.set_model('a', TableTemplate[MyRecordSchema])
    my_dataset.set_model('b', TableTemplate[MyRecordSchema])

    assert 'MyRecordSchema' in my_dataset.to_json_schema(pretty=True)
    assert 'MyOtherRecordSchema' in my_dataset.data['b'].to_json_schema(pretty=True)


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='specialize_record_models')
def test_specialize_record_models_signature_and_return_type_func(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):
    for flow_obj in case.flow_template, case.flow_template.apply():
        assert inspect.signature(flow_obj).parameters == {
            'tables':
                Parameter(
                    'tables',
                    Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=Dataset[GeneralTable],
                )
        }
        assert inspect.signature(flow_obj).return_annotation == MultiModelDataset[GeneralTable]


# TODO: Harmonize signature of job object and param_signatures mixin. Should both be used?


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='specialize_record_models')
def test_run_specialize_record_models_consistent_types(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        skip_test_if_dynamically_convert_elements_to_models,
        case: FlowCase):
    specialize_record_models = case.flow_template.apply()

    old_dataset = Dataset[GeneralTable]()
    old_dataset['a'] = [{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}]
    old_dataset['b'] = [{'b': 'df', 'c': True}, {'b': 'sg', 'c': False}]

    # general model allows the tables to be switched
    old_dataset['a'], old_dataset['b'] = old_dataset['b'], old_dataset['a']

    new_dataset = specialize_record_models(old_dataset)

    with pytest.raises(ValidationError):
        # per-table specialized models do not allow the tables to be switched
        new_dataset['a'], new_dataset['b'] = new_dataset['b'], new_dataset['a']

    assert_job_state(specialize_record_models, [RunState.FINISHED])


@pc.parametrize_with_cases('case', cases='.cases.flows', has_tag='specialize_record_models')
def test_fail_run_specialize_record_models_inconsistent_types(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
        case: FlowCase):

    specialize_record_models = case.flow_template.apply()

    old_dataset = Dataset[GeneralTable]()
    old_dataset['a'] = [{'a': 123, 'b': 'ads'}, {'a': 234, 'b': 'acs'}]
    old_dataset['b'] = [{'b': 'df', 'c': True}, {'b': False, 'c': 'sg'}]

    with pytest.raises(AssertionError):
        _new_dataset = specialize_record_models(old_dataset)  # noqa: F841
