from dataclasses import dataclass
from typing import Annotated, Any, Callable

import pytest
import pytest_cases as pc

from omnipy.components.json.typedefs import JsonScalar
from omnipy.components.tables.models import (ColumnWiseTableWithColNamesModel,
                                             CsvTableModel,
                                             CsvTableOfPydanticRecordsModel,
                                             IteratingPydanticRecordsModel,
                                             PydanticRecordModel,
                                             RowWiseTableFirstRowAsColNamesModel,
                                             RowWiseTableModel,
                                             RowWiseTableWithColNamesModel,
                                             TableOfPydanticRecordsModel,
                                             TsvTableModel)
from omnipy.data.model import Model
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util.pydantic import ValidationError
import omnipy.util.pydantic as pyd

from .cases.concat import ConcatCase, ConcatCaseReverse
from .cases.raw.asserts import assert_row_iter
from .cases.raw.table_data import column_wise_dict_of_lists_data

# TODO: Add tests and logic to check that all columns have the same length
#       in column-wise table models


def test_RowWise_table_without_col_names_model() -> None:
    row_wise_list_of_lists_data = [
        ['John', 'Doe', 30],
        ['Jane', 'Doe', 25],
    ]

    row_wise_table_without_col_names_model = RowWiseTableModel(row_wise_list_of_lists_data)
    assert row_wise_table_without_col_names_model.content == row_wise_list_of_lists_data
    assert row_wise_table_without_col_names_model.to_data() == row_wise_list_of_lists_data


def test_RowWise_table_without_col_names_model_empty() -> None:
    row_wise_table_without_col_names_model = RowWiseTableModel([])
    assert row_wise_table_without_col_names_model.content == []
    assert row_wise_table_without_col_names_model.to_data() == []


def test_columnwise_and_RowWise_table_models_with_col_names() -> None:
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

    row_wise_model = RowWiseTableWithColNamesModel(row_wise_data)
    assert row_wise_model.content == row_wise_data
    assert row_wise_model.to_data() == row_wise_data
    assert row_wise_model.col_names == ('a', 'b', 'c', 'd')

    column_wise_model = ColumnWiseTableWithColNamesModel(column_wise_data)
    assert column_wise_model.content == column_wise_data
    assert column_wise_model.to_data() == column_wise_data
    assert column_wise_model.col_names == ('a', 'b', 'c', 'd')

    converted_to_column_wise_model = ColumnWiseTableWithColNamesModel(row_wise_model)
    assert converted_to_column_wise_model.content == column_wise_data
    assert converted_to_column_wise_model.to_data() == column_wise_data
    assert converted_to_column_wise_model == column_wise_model
    assert converted_to_column_wise_model.col_names == ('a', 'b', 'c', 'd')

    row_wise_data_with_none = [
        {
            'a': '1', 'b': 2, 'c': True, 'd': None
        },
        {
            'a': '4', 'b': 5, 'c': None, 'd': 'abc'
        },
    ]
    converted_to_row_wise_model = RowWiseTableWithColNamesModel(column_wise_model)
    assert converted_to_row_wise_model.content == row_wise_data_with_none
    assert converted_to_row_wise_model.to_data() == row_wise_data_with_none
    assert converted_to_row_wise_model == RowWiseTableWithColNamesModel(row_wise_data_with_none)
    assert converted_to_row_wise_model.col_names == ('a', 'b', 'c', 'd')


def test_columnwise_and_RowWise_table_models_with_col_names_empty() -> None:
    row_wise_model = RowWiseTableWithColNamesModel([])
    assert row_wise_model.content == []
    assert row_wise_model.to_data() == []
    assert row_wise_model.col_names == ()

    column_wise_model = ColumnWiseTableWithColNamesModel({})
    assert column_wise_model.content == {}
    assert column_wise_model.to_data() == {}
    assert column_wise_model.col_names == ()

    converted_to_column_wise_model = ColumnWiseTableWithColNamesModel([])
    assert converted_to_column_wise_model.content == {}
    assert converted_to_column_wise_model.to_data() == {}
    assert converted_to_column_wise_model == column_wise_model
    assert converted_to_column_wise_model.col_names == ()

    converted_to_row_wise_model = RowWiseTableWithColNamesModel({})
    assert converted_to_row_wise_model.content == []
    assert converted_to_row_wise_model.to_data() == []
    assert converted_to_row_wise_model == row_wise_model
    assert converted_to_row_wise_model.col_names == ()


def test_columnwise_and_RowWise_table_models_failure() -> None:
    with pytest.raises(ValidationError):
        RowWiseTableWithColNamesModel(1)

    with pytest.raises(ValidationError):
        ColumnWiseTableWithColNamesModel(1)


def test_columnwise_table_iter(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    column_wise_model = ColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data)

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
    column_wise_model = ColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data)

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


def test_RowWise_table_first_row_as_col_names_model() -> None:
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


def test_RowWise_table_first_row_as_col_names_model_empty() -> None:
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


@pytest.fixture
def IteratingPersonModel() -> type[IteratingPydanticRecordsModel]:
    class PersonRecord(pyd.BaseModel):
        firstname: str
        lastname: str | None = ...  # type: ignore[assignment]
        age: int
        deceased: bool = False

    class IteratingPersonModel(IteratingPydanticRecordsModel[PersonRecord]):
        pass

    return IteratingPersonModel


def test_iterating_pydantic_record_model_column_wise_data(
        IteratingPersonModel: Annotated[type[IteratingPydanticRecordsModel],
                                        pytest.fixture]) -> None:
    persons = IteratingPersonModel(
        firstname=['John', 'Jane', 'Tarzan'],
        lastname=['Doe', 'Doe', None],
        age=['30', '25', '19'],
    )
    assert isinstance(persons.content, ColumnWiseTableWithColNamesModel)
    assert persons.to_data() == {
        'firstname': ['John', 'Jane', 'Tarzan'],
        'lastname': ['Doe', 'Doe', None],
        'age': [30, 25, 19],
        'deceased': [False, False, False],
    }
    tuple(persons.to_data().keys()) == (  # type: ignore[attr-defined]
        'firstname', 'lastname', 'age', 'deceased')

    with pytest.raises(ValidationError):
        IteratingPersonModel(firstname='Tarzan')

    with pytest.raises(ValidationError):
        IteratingPersonModel(firstname=['Tarzan'], age=['Unknown'])

    no_persons = IteratingPersonModel(firstname=[], lastname=[], age=[])
    assert isinstance(no_persons.content, ColumnWiseTableWithColNamesModel)
    assert no_persons.to_data() == {'firstname': [], 'lastname': [], 'age': []}

    empty_persons = IteratingPersonModel()
    assert isinstance(empty_persons.content, ColumnWiseTableWithColNamesModel)
    assert empty_persons.to_data() == {'firstname': [], 'lastname': [], 'age': []}


def test_iterating_pydantic_record_model_row_wise_data(
    # runtime: Annotated[IsRuntime, pytest.fixture],
    IteratingPersonModel: Annotated[type[IteratingPydanticRecordsModel], pytest.fixture]
) -> None:
    persons = IteratingPersonModel([
        ['John', 'Doe', '30'],
        ['Jane', 'Doe', '25'],
        ['Tarzan', None, '19'],
    ])
    assert isinstance(persons.content, ColumnWiseTableWithColNamesModel)
    assert persons.to_data() == {
        'firstname': ['John', 'Jane', 'Tarzan'],
        'lastname': ['Doe', 'Doe', None],
        'age': [30, 25, 19],
        'deceased': [False, False, False],
    }
    tuple(persons.to_data().keys()) == (  # type: ignore[attr-defined]
        'firstname', 'lastname', 'age', 'deceased')

    with pytest.raises(ValidationError):
        IteratingPersonModel([['Tarzan']])

    with pytest.raises(ValidationError):
        IteratingPersonModel([['Tarzan', None, 'Unknown']])

    no_persons = IteratingPersonModel([[], [], []])
    assert isinstance(no_persons.content, ColumnWiseTableWithColNamesModel)
    assert no_persons.to_data() == {'firstname': [], 'lastname': [], 'age': []}

    empty_persons = IteratingPersonModel()
    assert isinstance(empty_persons.content, ColumnWiseTableWithColNamesModel)
    assert empty_persons.to_data() == {'firstname': [], 'lastname': [], 'age': []}


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


@dataclass
class TableCase:
    model: type[Model]
    data: Any
    assert_func: Callable


@pc.fixture
def RowWiseRecordsTableModel() -> type[TableOfPydanticRecordsModel]:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    return TableOfNameRecordsModel


@pc.fixture
def CsvRowWiseRecordsTableModel() -> type[CsvTableOfPydanticRecordsModel]:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class CsvTableOfNameRecordsModel(CsvTableOfPydanticRecordsModel[NameRecord]):
        pass

    return CsvTableOfNameRecordsModel


@pc.fixture
def RowWiseRecordsTableOptionalLastModel() -> type[TableOfPydanticRecordsModel]:
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str
        age: int | None = None

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        ...

    return TableOfNameRecordsModel


@pc.fixture
def RowWise_data() -> Any:
    return [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


@pc.fixture
def RowWise_data_optional_last() -> Any:
    return [
        {
            'firstname': 'John', 'lastname': 'Doe', 'age': None
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe', 'age': 37
        },
    ]


@pc.fixture
def RowWise_records_assert(
        RowWise_data: Annotated[Any, pc.fixture]) -> Callable[[TableOfPydanticRecordsModel], None]:
    def _assert_func(table: TableOfPydanticRecordsModel) -> None:
        assert len(table) == 2
        assert isinstance(table[0], dict)
        assert isinstance(table[1], dict)

        assert table.to_data() == RowWise_data

    return _assert_func


@pc.fixture
def RowWise_pyd_records_assert(
        RowWise_data: Annotated[Any, pc.fixture]) -> Callable[[TableOfPydanticRecordsModel], None]:
    def _assert_func(table: TableOfPydanticRecordsModel) -> None:
        assert len(table) == 2
        assert isinstance(table[0], PydanticRecordModel)
        assert isinstance(table[1], PydanticRecordModel)

        assert table.to_data() == RowWise_data

    return _assert_func


@pc.fixture
def RowWise_pyd_records_optional_last_assert(
    RowWise_data_optional_last: Annotated[Any, pc.fixture]
) -> Callable[[TableOfPydanticRecordsModel], None]:
    def _assert_func(table: TableOfPydanticRecordsModel) -> None:
        assert len(table) == 2
        assert isinstance(table[0], PydanticRecordModel)
        assert isinstance(table[1], PydanticRecordModel)

        assert table.to_data() == RowWise_data_optional_last

    return _assert_func


@pc.case(id='RowWise_from_tsv', tags=['tables'])
def case_RowWise_from_tsv(
    RowWise_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                      pytest.fixture],
) -> TableCase:
    return TableCase(
        model=TsvTableModel,
        data='firstname\tlastname\nJohn\tDoe\nJane\tDoe\n',
        assert_func=RowWise_records_assert,
    )


@pc.case(id='RowWise_from_csv', tags=['tables'])
def case_RowWise_from_csv(
    RowWise_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                      pytest.fixture],
) -> TableCase:
    return TableCase(
        model=CsvTableModel,
        data='firstname,lastname\nJohn,Doe\nJane,Doe\n',
        assert_func=RowWise_records_assert,
    )


@pc.case(id='RowWise_pyd_from_records', tags=['tables'])
def case_RowWise_pyd_from_records(
    RowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    RowWise_data: Annotated[Any, pytest.fixture],
    RowWise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    return TableCase(
        model=RowWiseRecordsTableModel,
        data=RowWise_data,
        assert_func=RowWise_pyd_records_assert,
    )


@pc.case(id='RowWise_pyd_from_list_of_lists_table', tags=['tables'])
def case_RowWise_pyd_from_list_of_lists_table(
    RowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    RowWise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    return TableCase(
        model=RowWiseRecordsTableModel,
        data=[['John', 'Doe'], ['Jane', 'Doe']],
        assert_func=RowWise_pyd_records_assert)


@pc.case(id='RowWise_pyd_from_tsv', tags=['tables'])
def case_RowWise_pyd_from_tsv(
    RowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    RowWise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    return TableCase(
        model=RowWiseRecordsTableModel,
        data='John\tDoe\nJane\tDoe\n',
        assert_func=RowWise_pyd_records_assert)


@pc.case(id='csv_RowWise_pyd_from_tsv', tags=['tables'])
def case_RowWise_pyd_from_csv(
    CsvRowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    RowWise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    return TableCase(
        model=CsvRowWiseRecordsTableModel,
        data='John,Doe\nJane,Doe\n',
        assert_func=RowWise_pyd_records_assert)


@pc.case(id='RowWise_pyd_from_tsv_optional_field_last', tags=['tables'])
def case_RowWise_pyd_from_tsv_optional_last(
    RowWiseRecordsTableOptionalLastModel: Annotated[type[TableOfPydanticRecordsModel],
                                                    pytest.fixture],
    RowWise_pyd_records_optional_last_assert: Annotated[Callable[[TableOfPydanticRecordsModel],
                                                                 None],
                                                        pytest.fixture],
) -> TableCase:
    return TableCase(
        model=RowWiseRecordsTableOptionalLastModel,
        data='John\tDoe\nJane\tDoe\t37',
        assert_func=RowWise_pyd_records_optional_last_assert)


@pc.parametrize_with_cases('case', cases='.', has_tag='tables')
def test_table_of_tables_model(case: TableCase) -> None:
    case.assert_func(case.model(case.data))


def test_fail_table_of_records_model_with_optional_field_not_last() -> None:
    class OptionalNotLastRecord(pyd.BaseModel):
        firstname: str
        lastname: str | None = None
        age: int

    class TableOfOptionalNotLastRecord(TableOfPydanticRecordsModel[OptionalNotLastRecord]):
        ...

    with pytest.raises(ValidationError):
        TableOfOptionalNotLastRecord('Tarzan\t42\nJane\t37')


def test_fail_table_of_records_model_with_optional_fields_incorrect_input(
    RowWiseRecordsTableOptionalLastModel: Annotated[type[TableOfPydanticRecordsModel],
                                                    pytest.fixture]
) -> None:

    with pytest.raises(ValidationError):
        RowWiseRecordsTableOptionalLastModel('Tarzan')

    with pytest.raises(ValidationError):
        RowWiseRecordsTableOptionalLastModel('John\tDoe\t37\textra')


@pytest.mark.parametrize(
    'column_data', [[1, 2, 3], ['a', 'b', 'c'], [True, False, True], [1.0, 'abc', None]],
    ids=['integers', 'strings', 'booleans', 'mixed'])
def test_column_model(column_data: list[object]) -> None:
    from omnipy.components.tables.models import ColumnModel

    col = ColumnModel(column_data)
    assert col.content == column_data
    assert col.to_data() == column_data


def test_fail_column_model_invalid_input() -> None:
    from omnipy.components.tables.models import ColumnModel

    with pytest.raises(ValidationError):
        ColumnModel([1 + 2j])  # complex numbers are not JsonScalar
