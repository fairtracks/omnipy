from typing import Annotated

import pytest
import pytest_cases as pc
from scripts.type_alias_example import JsonScalar

from omnipy.components.tables.models import (ColumnWiseTableDictOfListsModel,
                                             PydanticRecordModel,
                                             RowWiseTableFirstRowAsColNamesModel,
                                             RowWiseTableListOfDictsModel,
                                             TableOfPydanticRecordsModel)
from omnipy.data.model import Model
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util._pydantic import ValidationError
import omnipy.util._pydantic as pyd

from .cases.concat import ConcatCase, ConcatCaseReverse
from .cases.raw.asserts import assert_row_iter
from .cases.raw.table_data import column_wise_dict_of_lists_data

# TODO: Add tests and logic to check that all columns have the same length
#       in column-wise table models


def test_columnwise_and_rowwise_table_models_with_col_names() -> None:
    row_wise_data = [
        {
            'a': '1', 'b': 2, 'c': True
        },
        {
            'a': '4', 'b': 5, 'd': 'abc'
        },
    ]
    column_wise_data = {
        'a': ['1', '4'],
        'b': [2, 5],
        'c': [True, None],
        'd': [None, 'abc'],
    }

    row_wise_model = RowWiseTableListOfDictsModel(row_wise_data)
    assert row_wise_model.content == row_wise_data
    assert row_wise_model.to_data() == row_wise_data

    column_wise_model = ColumnWiseTableDictOfListsModel(column_wise_data)
    assert column_wise_model.content == column_wise_data
    assert column_wise_model.to_data() == column_wise_data

    converted_to_column_wise_model = ColumnWiseTableDictOfListsModel(row_wise_model)
    assert converted_to_column_wise_model.content == column_wise_data
    assert converted_to_column_wise_model.to_data() == column_wise_data
    assert converted_to_column_wise_model == column_wise_model

    row_wise_data_with_none = [
        {
            'a': '1', 'b': 2, 'c': True, 'd': None
        },
        {
            'a': '4', 'b': 5, 'c': None, 'd': 'abc'
        },
    ]
    converted_to_row_wise_model = RowWiseTableListOfDictsModel(column_wise_model)
    assert converted_to_row_wise_model.content == row_wise_data_with_none
    assert converted_to_row_wise_model.to_data() == row_wise_data_with_none
    assert converted_to_row_wise_model == RowWiseTableListOfDictsModel(row_wise_data_with_none)


def test_columnwise_and_rowwise_table_models_with_col_names_empty() -> None:
    row_wise_model = RowWiseTableListOfDictsModel([])
    assert row_wise_model.content == []
    assert row_wise_model.to_data() == []

    column_wise_model = ColumnWiseTableDictOfListsModel({})
    assert column_wise_model.content == {}
    assert column_wise_model.to_data() == {}

    converted_to_column_wise_model = ColumnWiseTableDictOfListsModel([])
    assert converted_to_column_wise_model.content == {}
    assert converted_to_column_wise_model.to_data() == {}
    assert converted_to_column_wise_model == column_wise_model

    converted_to_row_wise_model = RowWiseTableListOfDictsModel({})
    assert converted_to_row_wise_model.content == []
    assert converted_to_row_wise_model.to_data() == []
    assert converted_to_row_wise_model == row_wise_model


def test_columnwise_and_rowwise_table_models_failure() -> None:
    with pytest.raises(ValidationError):
        RowWiseTableListOfDictsModel(1)

    with pytest.raises(ValidationError):
        ColumnWiseTableDictOfListsModel(1)


def test_columnwise_table_iter(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    column_wise_model = ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data)

    for i, row in enumerate(column_wise_model):
        assert_row_iter(i, row)

    def model_content_if_needed(model_or_obj):
        return model_or_obj.content if is_model_instance(model_or_obj) else model_or_obj

    assert tuple(column_wise_model.keys()) == ('a', 'b', 'c', 'd')
    assert tuple(model_content_if_needed(_) for _ in column_wise_model.values()) == (
        ['1', '4'],
        [2, 5],
        [True, None],
        [None, 'abc'],
    )

    assert len(column_wise_model) == 2
    rows = list(column_wise_model)
    assert len(rows) == 2

    # The rows are the same object reused for each iteration
    assert rows[0] == rows[1]
    assert id(rows[0]) == id(rows[1])

    # But can still be extracted using a Model and an iterator
    extracted = Model[list[dict[str, JsonScalar]]](iter(column_wise_model))
    assert extracted.to_data() == [
        {
            'a': '1', 'b': 2, 'c': True, 'd': None
        },
        {
            'a': '4', 'b': 5, 'c': None, 'd': 'abc'
        },
    ]

    # Without iter(), a new Model will consider the column-wise data as a whole
    extracted_whole = Model[dict[str, list[JsonScalar]]](column_wise_model)
    assert extracted_whole.to_data() == column_wise_dict_of_lists_data


def test_columnwise_table_index(runtime: Annotated[IsRuntime, pytest.fixture],) -> None:
    column_wise_model = ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data)

    assert len(column_wise_model) == 2

    assert_row_iter(0, column_wise_model[0])
    assert_row_iter(1, column_wise_model[1])

    with pytest.raises(IndexError):
        column_wise_model[2]

    with pytest.raises(ValidationError):
        column_wise_model[1] = {'a': '2', 'b': 3, 'c': False, 'd': 'def'}  # type: ignore

    if not runtime.config.data.model.interactive:
        del column_wise_model[1]  # type: ignore

    assert column_wise_model['a'] == ['1', '4']
    column_wise_model['a'] = ['10', '40']
    assert column_wise_model[1]['a'] == '40'


@pc.parametrize_with_cases(
    'case',
    cases='.cases.concat',
    has_tag='concat',
)
def test_columnwise_table_concatenate_add(case: ConcatCase) -> None:
    concat_model = case.col_wise_model + case.other
    assert concat_model.to_data() == case.expected


@pc.parametrize_with_cases(
    'case',
    cases='.cases.concat',
    has_tag='concat',
)
def test_columnwise_table_concatenate_inplace_add(case: ConcatCase) -> None:
    concat_model = case.col_wise_model
    concat_model += case.other
    assert concat_model.to_data() == case.expected


@pc.parametrize_with_cases(
    'case',
    cases='.cases.concat',
    has_tag=['concat', 'reverse'],
)
def test_columnwise_table_reverse_concatenate_add(case: ConcatCaseReverse) -> None:
    concat_model = case.other + case.col_wise_model
    assert concat_model.to_data() == case.expected_reverse


def test_row_wise_table_first_row_as_col_names_model() -> None:
    row_wise_list_of_lists_data = [
        ['firstname', 'lastname'],
        ['John', 'Doe'],
        ['Jane', 'Doe'],
    ]

    row_wise_list_of_dicts_data = [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]

    row_wise_table_with_col_names_model = RowWiseTableFirstRowAsColNamesModel(
        row_wise_list_of_lists_data)
    assert row_wise_table_with_col_names_model.content == row_wise_list_of_dicts_data
    assert row_wise_table_with_col_names_model.to_data() == row_wise_list_of_dicts_data
    assert row_wise_table_with_col_names_model.col_names == ('firstname', 'lastname')


def test_row_wise_table_first_row_as_col_names_model_empty() -> None:
    row_wise_table_with_col_names_model = RowWiseTableFirstRowAsColNamesModel([])
    assert row_wise_table_with_col_names_model.content == []
    assert row_wise_table_with_col_names_model.to_data() == []
    assert row_wise_table_with_col_names_model.col_names == ()

    row_wise_table_with_col_names_model = RowWiseTableFirstRowAsColNamesModel(
        [['firstname', 'lastname']])
    assert row_wise_table_with_col_names_model.content == []
    assert row_wise_table_with_col_names_model.to_data() == []
    # At least one data row is needed to store column names
    assert row_wise_table_with_col_names_model.col_names == ()


def test_pydantic_record_model_all_required() -> None:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class NameRecordModel(PydanticRecordModel[NameRecord]):
        pass

    record = NameRecordModel(firstname='John', lastname='Doe')
    assert record.content == NameRecord(firstname='John', lastname='Doe')
    assert record.to_data() == {'firstname': 'John', 'lastname': 'Doe'}

    record = NameRecordModel({'firstname': 'Jane', 'lastname': 'Doe'})
    assert record.content == NameRecord(firstname='Jane', lastname='Doe')
    assert record.to_data() == {'firstname': 'Jane', 'lastname': 'Doe'}

    record = NameRecordModel(NameRecord(firstname='Robert', lastname='Doe'))
    assert record.content == NameRecord(firstname='Robert', lastname='Doe')
    assert record.to_data() == {'firstname': 'Robert', 'lastname': 'Doe'}

    record = NameRecordModel(['Emily', 'Doe'])
    assert record.content == NameRecord(firstname='Emily', lastname='Doe')
    assert record.to_data() == {'firstname': 'Emily', 'lastname': 'Doe'}

    with pytest.raises(ValidationError):
        NameRecordModel(firstname='Tarzan')


def test_pydantic_record_model_optional() -> None:
    class NameRecordOptionalLastName(pyd.BaseModel):
        firstname: str
        lastname: str | None = None

    class NameRecordOptionalLastNameModel(PydanticRecordModel[NameRecordOptionalLastName]):
        pass

    record = NameRecordOptionalLastNameModel(firstname='Tarzan')
    assert record.content == NameRecordOptionalLastName(firstname='Tarzan')
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None}

    record = NameRecordOptionalLastNameModel(['Tarzan', None])
    assert record.content == NameRecordOptionalLastName(firstname='Tarzan')
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None}

    NameRecordOptionalLastNameModel(firstname='Tarzan', title='King of Apes')
    assert record.content == NameRecordOptionalLastName(firstname='Tarzan')
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None}


def test_pydantic_record_model_extra_fields_config() -> None:
    class NameRecordNoExtraFields(pyd.BaseModel):
        firstname: str
        lastname: str | None = None

        class Config:
            extra = 'forbid'

    class NameRecordNoExtraFieldsModel(PydanticRecordModel[NameRecordNoExtraFields]):
        pass

    with pytest.raises(ValidationError):
        NameRecordNoExtraFieldsModel(firstname='Tarzan', title='King of Apes')

    class NameRecordExtraFields(pyd.BaseModel):
        firstname: str
        lastname: str | None = None

        class Config:
            extra = 'allow'

    class NameRecordExtraFieldsModel(PydanticRecordModel[NameRecordExtraFields]):
        pass

    record = NameRecordExtraFieldsModel(firstname='Tarzan', title='King of Apes')
    assert record.content == NameRecordExtraFields(
        firstname='Tarzan',
        title='King of Apes',  # type: ignore[call-arg]
    )
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None, 'title': 'King of Apes'}


def test_table_of_pydantic_records_model_from_list_of_dicts() -> None:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    table = TableOfNameRecordsModel([
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ])

    assert len(table) == 2
    assert isinstance(table[0], PydanticRecordModel)
    assert isinstance(table[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


def test_table_of_pydantic_records_model_from_list_of_lists() -> None:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    table = TableOfNameRecordsModel([
        ['John', 'Doe'],
        ['Jane', 'Doe'],
    ])

    assert len(table) == 2
    assert isinstance(table[0], PydanticRecordModel)
    assert isinstance(table[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


def test_table_of_pydantic_records_model_from_str() -> None:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    table = TableOfNameRecordsModel('John\tDoe\nJane\tDoe')

    assert len(table) == 2
    assert isinstance(table[0], PydanticRecordModel)
    assert isinstance(table[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


def test_table_of_pydantic_records_model_with_optional_fields_not_last() -> None:
    class OptionalNotLastRecord(pyd.BaseModel):
        firstname: str
        lastname: str | None = None
        age: int

    class TableOfOptionalNotLastRecord(TableOfPydanticRecordsModel[OptionalNotLastRecord]):
        ...

    with pytest.raises(ValidationError):
        TableOfOptionalNotLastRecord('Tarzan\t42\nJane\t37')


def test_table_of_pydantic_records_model_with_optional_fields_last() -> None:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str
        age: int | None = None

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        ...

    table = TableOfNameRecordsModel('John\tDoe\nJane\tDoe\t37')

    assert len(table) == 2
    assert isinstance(table[0], PydanticRecordModel)
    assert isinstance(table[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe', 'age': None
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe', 'age': 37
        },
    ]

    with pytest.raises(ValidationError):
        TableOfNameRecordsModel('Tarzan')

    with pytest.raises(ValidationError):
        TableOfNameRecordsModel('John\tDoe\t37\textra')
