import pytest

from omnipy.components.tables.models import (ColumnWiseTableDictOfListsModel,
                                             PydanticRecordModel,
                                             RowWiseTableFirstRowAsColNamesModel,
                                             RowWiseTableListOfDictsModel,
                                             TableOfPydanticRecordsModel)
from omnipy.util._pydantic import ValidationError
import omnipy.util._pydantic as pyd

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
