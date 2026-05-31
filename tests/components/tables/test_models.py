"""Tests for table models and pydantic-backed records."""

from dataclasses import dataclass
import math
from typing import Annotated, Any, Callable, cast, Generic

import pytest
import pytest_cases as pc
from typing_extensions import TypeVar

from omnipy.components.json.typedefs import JsonDictOfScalars, JsonListOfScalars, JsonScalar
from omnipy.components.tables.models import (ColumnModel,
                                             ColumnWiseTableWithColNamesModel,
                                             CsvTableModel,
                                             CsvTableOfPydanticRecordsModel,
                                             IteratingPydanticRecordsModel,
                                             JsonMaxLevel1ColumnModel,
                                             JsonMaxLevel1ColumnWiseTableWithColNamesModel,
                                             JsonMaxLevel2ColumnModel,
                                             JsonMaxLevel2ColumnWiseTableWithColNamesModel,
                                             JsonScalarColumnModel,
                                             JsonScalarColumnWiseTableWithColNamesModel,
                                             PydanticRecordModel,
                                             PydanticRecordModelBase,
                                             RowWiseTableFirstRowAsColNamesModel,
                                             RowWiseTableModel,
                                             RowWiseTableWithColNamesModel,
                                             TableOfPydanticRecordsModel,
                                             TsvTableModel)
from omnipy.data.model import is_model_instance, Model
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util.pydantic import ValidationError
import omnipy.util.pydantic as pyd

from .cases.concat import ConcatCase, ConcatCaseReverse
from .cases.raw.table_data import column_wise_dict_of_lists_data
from .helpers.classes import IntListLikeColumnModel, ListLikeNoAdd
from .helpers.protocols import AssertColumnWiseMappings, AssertRowIter

# TODO: Add tests and logic to check that all columns have the same length
#       in column-wise table models


def test_rowwise_table_without_col_names_model() -> None:
    row_wise_list_of_lists_data = [
        ['John', 'Doe', 30],
        ['Jane', 'Doe', 25],
    ]

    row_wise_table_without_col_names_model = RowWiseTableModel(row_wise_list_of_lists_data)
    assert row_wise_table_without_col_names_model.content == row_wise_list_of_lists_data
    assert row_wise_table_without_col_names_model.to_data() == row_wise_list_of_lists_data


def test_rowwise_table_without_col_names_model_empty() -> None:
    row_wise_table_without_col_names_model = RowWiseTableModel([])
    assert row_wise_table_without_col_names_model.content == []
    assert row_wise_table_without_col_names_model.to_data() == []


def test_columnwise_and_rowwise_table_models_with_col_names(
        assert_column_wise_mappings: Annotated[AssertColumnWiseMappings, pytest.fixture]) -> None:
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

    column_wise_model = JsonScalarColumnWiseTableWithColNamesModel(column_wise_data)
    assert_column_wise_mappings(column_wise_model, column_wise_data)
    assert column_wise_model.to_data() == column_wise_data
    assert column_wise_model.col_names == ('a', 'b', 'c', 'd')

    converted_to_column_wise_model = JsonScalarColumnWiseTableWithColNamesModel(row_wise_model)
    assert_column_wise_mappings(converted_to_column_wise_model, column_wise_data)
    assert converted_to_column_wise_model.to_data() == column_wise_data
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


def test_columnwise_and_rowwise_table_models_with_col_names_empty() -> None:
    row_wise_model = RowWiseTableWithColNamesModel([])
    assert row_wise_model.content == []
    assert row_wise_model.to_data() == []
    assert row_wise_model.col_names == ()

    column_wise_model = JsonScalarColumnWiseTableWithColNamesModel({})
    assert column_wise_model.content == {}
    assert column_wise_model.to_data() == {}
    assert column_wise_model.col_names == ()

    converted_to_column_wise_model = JsonScalarColumnWiseTableWithColNamesModel([])
    assert converted_to_column_wise_model.content == {}
    assert converted_to_column_wise_model.to_data() == {}
    assert converted_to_column_wise_model == column_wise_model
    assert converted_to_column_wise_model.col_names == ()

    converted_to_row_wise_model = RowWiseTableWithColNamesModel({})
    assert converted_to_row_wise_model.content == []
    assert converted_to_row_wise_model.to_data() == []
    assert converted_to_row_wise_model == row_wise_model
    assert converted_to_row_wise_model.col_names == ()


def test_columnwise_and_rowwise_table_models_failure() -> None:
    with pytest.raises(ValidationError):
        RowWiseTableWithColNamesModel(1)

    with pytest.raises(ValidationError):
        JsonScalarColumnWiseTableWithColNamesModel(1)


def test_columnwise_table_iter(assert_row_iter: Annotated[AssertRowIter, pytest.fixture]) -> None:
    column_wise_model = JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data)

    for i in range(len(column_wise_model)):
        assert_row_iter(i, column_wise_model[i])

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


def test_columnwise_table_index(
    runtime: Annotated[IsRuntime, pytest.fixture],
    assert_row_iter: Annotated[AssertRowIter, pytest.fixture],
) -> None:
    column_wise_model = JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data)

    assert len(column_wise_model) == 2

    assert_row_iter(0, column_wise_model[0])
    assert_row_iter(1, column_wise_model[1])

    with pytest.raises(IndexError):
        column_wise_model[2]

    with pytest.raises(ValidationError):
        column_wise_model[1] = {'a': '2', 'b': 3, 'c': False, 'd': 'def'}  # type: ignore

    if not runtime.config.data.model.interactive:
        del column_wise_model[1]  # type: ignore

    assert column_wise_model['a'].to_data() == ['1', '4']
    column_wise_model['a'] = ['10', '40']
    assert column_wise_model[1]['a'] == '40'


@pc.parametrize_with_cases(
    'case',
    cases='.cases.concat',
    has_tag='concat',
)
def test_columnwise_table_concatenate_add(case: ConcatCase) -> None:
    """Test concatenating column-wise tables with addition."""
    concat_model = case.col_wise_model + case.other
    assert concat_model.to_data() == case.expected


@pc.parametrize_with_cases(
    'case',
    cases='.cases.concat',
    has_tag='concat',
)
def test_columnwise_table_concatenate_inplace_add(case: ConcatCase) -> None:
    """Test concatenating column-wise tables with in-place addition."""
    concat_model = case.col_wise_model
    concat_model += case.other
    assert concat_model.to_data() == case.expected


@pc.parametrize_with_cases(
    'case',
    cases='.cases.concat',
    has_tag=['concat', 'reverse'],
)
def test_columnwise_table_reverse_concatenate_add(case: ConcatCaseReverse) -> None:
    """Test reverse-add concatenation for column-wise tables."""
    concat_model = case.other + case.col_wise_model
    assert concat_model.to_data() == case.expected_reverse


def test_rowwise_table_first_row_as_col_names_model() -> None:
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


def test_rowwise_table_first_row_as_col_names_model_empty() -> None:
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
    """Test pydantic record models with all required fields."""
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


class PersonRecord(pyd.BaseModel):
    firstname: str
    lastname: str | None = ...  # type: ignore[assignment]
    age: int
    deceased: bool = False


class IteratingPersonModel(IteratingPydanticRecordsModel[
        PersonRecord,
        JsonScalarColumnWiseTableWithColNamesModel,
        JsonScalarColumnModel,
        JsonScalar,
]):
    pass


def test_iterating_pydantic_record_model_column_wise_data() -> None:
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


def test_iterating_pydantic_record_model_header_info_tracks_output_type() -> None:
    header_info = cast(Any, IteratingPersonModel).header_info
    assert header_info.data_with_col_names_type is JsonScalarColumnWiseTableWithColNamesModel


def test_iterating_pydantic_record_model_model_instance_input_uses_content_type() -> None:
    source_data = JsonScalarColumnWiseTableWithColNamesModel(
        firstname=['John', 'Jane'],
        lastname=['Doe', 'Doe'],
        age=['30', '25'],
    )

    persons = IteratingPersonModel(source_data)

    assert isinstance(persons.content, JsonScalarColumnWiseTableWithColNamesModel)
    assert persons.to_data() == {
        'firstname': ['John', 'Jane'],
        'lastname': ['Doe', 'Doe'],
        'age': [30, 25],
        'deceased': [False, False],
    }


def test_iterating_pydantic_record_model_row_wise_uses_declared_output_type() -> None:
    class MaxLevel1PersonRecord(pyd.BaseModel):
        firstname: str
        age: int

    class IteratingPersonMaxLevel1Model(
            IteratingPydanticRecordsModel[MaxLevel1PersonRecord,
                                          JsonMaxLevel1ColumnWiseTableWithColNamesModel,
                                          JsonMaxLevel1ColumnModel,
                                          JsonScalar | JsonDictOfScalars | JsonListOfScalars]):
        pass

    persons = IteratingPersonMaxLevel1Model([
        ['John', '30'],
        ['Jane', '25'],
    ])

    assert isinstance(persons.content, JsonMaxLevel1ColumnWiseTableWithColNamesModel)
    assert persons.to_data() == {
        'firstname': ['John', 'Jane'],
        'age': [30, 25],
    }


def test_iterating_pydantic_record_model_row_wise_data(
        # runtime: Annotated[IsRuntime, pytest.fixture],
) -> None:
    """Test iterating pydantic record models from row-wise input."""
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
    """Test pydantic record models with optional fields."""
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


def test_pydantic_record_model_raises_type_error_for_unsupported_input_type() -> None:
    class AnyRecord(pyd.BaseModel):
        value: int

    class AnyRecordModel(PydanticRecordModel[AnyRecord]):
        pass

    with pytest.raises(TypeError, match='Unsupported data type'):
        AnyRecordModel._parse_data(123)  # type: ignore[arg-type]


def test_pydantic_record_model_base_forwards_output_type_to_row_parser() -> None:
    class AnyRecord(pyd.BaseModel):
        value: int

    class AnyRecordModel(PydanticRecordModelBase[
            AnyRecord,
            JsonScalarColumnWiseTableWithColNamesModel,
            list[JsonScalar],
    ]):
        _seen_output_type: type[JsonScalarColumnWiseTableWithColNamesModel] | None = None

        @classmethod
        def _validate_record_model_with_col_names(
            cls,
            pyd_model: type[pyd.BaseModel],
            data: JsonScalarColumnWiseTableWithColNamesModel,
            header_names: tuple[str, ...],
        ) -> pyd.BaseModel | JsonScalarColumnWiseTableWithColNamesModel:
            return cast(JsonScalarColumnWiseTableWithColNamesModel, data)

        @classmethod
        def _validate_record_model_without_col_names(
            cls,
            pyd_model: type[pyd.BaseModel],
            data: list[JsonScalar],
            output_type: type[JsonScalarColumnWiseTableWithColNamesModel],
            header_names: tuple[str, ...],
        ) -> pyd.BaseModel | JsonScalarColumnWiseTableWithColNamesModel:
            concrete_output_type = cast(type[JsonScalarColumnWiseTableWithColNamesModel],
                                        output_type)
            cls._seen_output_type = concrete_output_type
            return concrete_output_type({'value': [int(cast(int | str, data[0]))]})

    model_obj = AnyRecordModel(['3'])

    assert AnyRecordModel._seen_output_type is JsonScalarColumnWiseTableWithColNamesModel
    assert isinstance(model_obj.content, JsonScalarColumnWiseTableWithColNamesModel)
    assert model_obj.to_data() == {'value': [3]}


def test_pydantic_record_model_extra_fields_config() -> None:
    """Test pydantic record models honoring extra-field config."""
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
    """Return a table model for required name records."""
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    return TableOfNameRecordsModel


@pc.fixture
def CsvRowWiseRecordsTableModel() -> type[CsvTableOfPydanticRecordsModel]:
    """Return a CSV-backed table model for required name records."""
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str

    class CsvTableOfNameRecordsModel(CsvTableOfPydanticRecordsModel[NameRecord]):
        pass

    return CsvTableOfNameRecordsModel


@pc.fixture
def RowWiseRecordsTableOptionalLastModel() -> type[TableOfPydanticRecordsModel]:
    """Return a table model for name records with an optional age."""
    class NameRecord(pyd.BaseModel):
        firstname: str
        lastname: str
        age: int | None = None

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        ...

    return TableOfNameRecordsModel


@pc.fixture
def rowwise_data() -> Any:
    return [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


@pc.fixture
def rowwise_data_optional_last() -> Any:
    return [
        {
            'firstname': 'John', 'lastname': 'Doe', 'age': None
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe', 'age': 37
        },
    ]


@pc.fixture
def rowwise_records_assert(
    rowwise_data: Annotated[Any,
                            pc.fixture]) -> Callable[[RowWiseTableFirstRowAsColNamesModel], None]:
    """Return an assertion helper for plain row-wise record tables."""
    def _assert_func(table: RowWiseTableFirstRowAsColNamesModel) -> None:
        assert len(table) == 2

        for row in table:
            if table.config.model.dynamically_convert_elements_to_models:
                assert is_model_instance(row) and isinstance(row.content, dict)
            else:
                assert isinstance(row, dict)

        assert table.to_data() == rowwise_data

    return _assert_func


@pc.fixture
def rowwise_pyd_records_assert(
        rowwise_data: Annotated[Any, pc.fixture]) -> Callable[[TableOfPydanticRecordsModel], None]:
    def _assert_func(table: TableOfPydanticRecordsModel) -> None:
        assert len(table) == 2
        assert isinstance(table[0], PydanticRecordModel)
        assert isinstance(table[1], PydanticRecordModel)

        assert table.to_data() == rowwise_data

    return _assert_func


@pc.fixture
def rowwise_pyd_records_optional_last_assert(
    rowwise_data_optional_last: Annotated[Any, pc.fixture]
) -> Callable[[TableOfPydanticRecordsModel], None]:
    """Return an assertion helper for optional-age record tables."""
    def _assert_func(table: TableOfPydanticRecordsModel) -> None:
        assert len(table) == 2
        assert isinstance(table[0], PydanticRecordModel)
        assert isinstance(table[1], PydanticRecordModel)

        assert table.to_data() == rowwise_data_optional_last

    return _assert_func


@pc.case(id='rowwise_from_tsv', tags=['tables'])
def case_rowwise_from_tsv(
    rowwise_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                      pytest.fixture],
) -> TableCase:
    """Return a TSV case for plain row-wise table parsing."""
    return TableCase(
        model=TsvTableModel,
        data='firstname\tlastname\nJohn\tDoe\nJane\tDoe\n',
        assert_func=rowwise_records_assert,
    )


@pc.case(id='rowwise_from_csv', tags=['tables'])
def case_rowwise_from_csv(
    rowwise_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                      pytest.fixture],
) -> TableCase:
    """Return a CSV case for plain row-wise table parsing."""
    return TableCase(
        model=CsvTableModel,
        data='firstname,lastname\nJohn,Doe\nJane,Doe\n',
        assert_func=rowwise_records_assert,
    )


@pc.case(id='rowwise_pyd_from_records', tags=['tables'])
def case_rowwise_pyd_from_records(
    RowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    rowwise_data: Annotated[Any, pytest.fixture],
    rowwise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    """Return a pydantic-record case from row-wise dictionaries."""
    return TableCase(
        model=RowWiseRecordsTableModel,
        data=rowwise_data,
        assert_func=rowwise_pyd_records_assert,
    )


@pc.case(id='rowwise_pyd_from_list_of_lists_table', tags=['tables'])
def case_rowwise_pyd_from_list_of_lists_table(
    RowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    rowwise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    """Return a pydantic-record case from row-wise lists."""
    return TableCase(
        model=RowWiseRecordsTableModel,
        data=[['John', 'Doe'], ['Jane', 'Doe']],
        assert_func=rowwise_pyd_records_assert)


@pc.case(id='rowwise_pyd_from_tsv', tags=['tables'])
def case_rowwise_pyd_from_tsv(
    RowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    rowwise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    """Return a pydantic-record case from TSV text."""
    return TableCase(
        model=RowWiseRecordsTableModel,
        data='John\tDoe\nJane\tDoe\n',
        assert_func=rowwise_pyd_records_assert)


@pc.case(id='csv_rowwise_pyd_from_tsv', tags=['tables'])
def case_rowwise_pyd_from_csv(
    CsvRowWiseRecordsTableModel: Annotated[type[TableOfPydanticRecordsModel], pytest.fixture],
    rowwise_pyd_records_assert: Annotated[Callable[[TableOfPydanticRecordsModel], None],
                                          pytest.fixture],
) -> TableCase:
    """Return a pydantic-record case from CSV text."""
    return TableCase(
        model=CsvRowWiseRecordsTableModel,
        data='John,Doe\nJane,Doe\n',
        assert_func=rowwise_pyd_records_assert)


@pc.case(id='rowwise_pyd_from_tsv_optional_field_last', tags=['tables'])
def case_rowwise_pyd_from_tsv_optional_last(
    RowWiseRecordsTableOptionalLastModel: Annotated[type[TableOfPydanticRecordsModel],
                                                    pytest.fixture],
    rowwise_pyd_records_optional_last_assert: Annotated[Callable[[TableOfPydanticRecordsModel],
                                                                 None],
                                                        pytest.fixture],
) -> TableCase:
    """Return a pydantic-record case with an optional trailing field."""
    return TableCase(
        model=RowWiseRecordsTableOptionalLastModel,
        data='John\tDoe\nJane\tDoe\t37',
        assert_func=rowwise_pyd_records_optional_last_assert)


@pc.parametrize_with_cases('case', cases='.', has_tag='tables')
def test_table_of_tables_model(case: TableCase) -> None:
    """Test table model cases built from the parametrized fixtures."""
    case.assert_func(case.model(case.data))


def test_fail_table_of_records_model_with_optional_field_not_last() -> None:
    """Test record tables reject optional fields before required ones."""
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
    """Test record tables reject malformed optional-field input rows."""

    with pytest.raises(ValidationError):
        RowWiseRecordsTableOptionalLastModel('Tarzan')

    with pytest.raises(ValidationError):
        RowWiseRecordsTableOptionalLastModel('John\tDoe\t37\textra')


def test_column_model_default_value() -> None:
    class MyClass:
        ...

    T = TypeVar('T')

    class MyList(list[T], Generic[T]):
        ...

    assert ColumnModel[list[int], int].default_value() == 0
    assert ColumnModel[tuple[bool, ...], bool].default_value() is False
    assert ColumnModel[list[list[int]], list[int]].default_value() == []
    assert ColumnModel[MyList[int], int].default_value() == 0
    assert isinstance(ColumnModel[tuple[MyClass, ...], MyClass].default_value(), MyClass)

    assert ColumnModel[list[float | None], float | None].default_value() is None
    assert math.isnan(ColumnModel[list[int | float], int | float].default_value())
    assert ColumnModel[list[str | int], str | int].default_value() == 0
    assert ColumnModel[list[list[int] | str], list[int] | str].default_value() == ''
    assert ColumnModel[list[dict[str, int] | list[int]],
                       dict[str, int] | list[int]].default_value() == []
    assert ColumnModel[list[set[int] | dict[str, int]],
                       set[int] | dict[str, int]].default_value() == {}
    assert ColumnModel[list[bool | set[int]], bool | set[int]].default_value() == set()


def test_column_model_default_filled() -> None:
    T = TypeVar('T')

    class MyList(list[T], Generic[T]):
        ...

    assert ColumnModel[list[int], int].filled(0, 0).to_data() == []
    assert ColumnModel[list[int], int].filled(0, 1).to_data() == [0]
    assert ColumnModel[MyList[int], int].filled(1, 10).to_data() == MyList([1]) * 10

    assert ColumnModel[tuple[str | float, ...], str | float].filled(0.0,
                                                                    3).to_data() == (0.0, 0.0, 0.0)

    class MyListOfListsColumnModel(ColumnModel[list[list[object]], list[object]]):
        ...

    my_pair_list_of_lists_model = MyListOfListsColumnModel.filled([], 2)
    assert isinstance(my_pair_list_of_lists_model, MyListOfListsColumnModel)
    assert len(my_pair_list_of_lists_model) == 2
    assert my_pair_list_of_lists_model.content[0] == []
    assert my_pair_list_of_lists_model.content[1] == []


@pytest.mark.parametrize('method_name', ('default_value', 'filled'))
def test_fail_column_model_default_value_or_filled(method_name: str) -> None:

    with pytest.raises(TypeError):
        getattr(ColumnModel[tuple[int], int], method_name)()

    with pytest.raises(TypeError):
        getattr(ColumnModel[list[bool | complex], bool | complex], method_name)()

    class MyIntList(list[int]):
        ...

    with pytest.raises(TypeError):
        getattr(ColumnModel[MyIntList, int], method_name)()

    with pytest.raises(TypeError):
        getattr(ColumnModel[list[int] | tuple[int, ...], int], method_name)()


@pytest.mark.parametrize(
    'column_data', [[1, 2, 3], ['a', 'b', 'c'], [True, False, True], [1.0, 'abc', None]],
    ids=['integers', 'strings', 'booleans', 'mixed'])
def test_json_scalar_column_model(column_data: list[object]) -> None:
    col = JsonScalarColumnModel(column_data)
    assert col.content == column_data
    assert col.to_data() == column_data


def test_json_scalar_column_model_default_value_and_filled() -> None:
    assert JsonScalarColumnModel.default_value() is None
    assert JsonScalarColumnModel.filled(None, 0) == JsonScalarColumnModel([])
    assert JsonScalarColumnModel.filled(None, 1) == JsonScalarColumnModel([None])
    assert JsonScalarColumnModel.filled(None, 10) == JsonScalarColumnModel([None] * 10)
    assert JsonScalarColumnModel.filled(0, 10) == JsonScalarColumnModel([0] * 10)


def test_fail_json_scalar_column_model_invalid_input() -> None:
    with pytest.raises(ValidationError):
        JsonScalarColumnModel([1 + 2j])  # complex numbers are not JsonScalar


def test_column_model_concat_operators_for_tuple_content() -> None:
    class TupleColumnModel(ColumnModel[tuple[int, ...], int]):
        ...

    col = TupleColumnModel((1, 2))
    other = TupleColumnModel((3, 4))

    assert (col + other) == TupleColumnModel((1, 2, 3, 4))
    assert (3, 4) + col == TupleColumnModel((3, 4, 1, 2))

    col += other
    assert col == TupleColumnModel((1, 2, 3, 4))


def test_column_model_concat_operators_for_adapted_array_content() -> None:
    a = ListLikeNoAdd([1, 2])
    b = ListLikeNoAdd([3, 4])

    with pytest.raises(TypeError):
        a + b  # type: ignore[operator]

    assert IntListLikeColumnModel(a) + b == IntListLikeColumnModel([1, 2, 3, 4])
    assert a + IntListLikeColumnModel(b) == IntListLikeColumnModel([1, 2, 3, 4])
    assert IntListLikeColumnModel(a) + IntListLikeColumnModel(b) \
           == IntListLikeColumnModel([1, 2, 3, 4])

    a_model = IntListLikeColumnModel(a)
    a_model += b
    assert a_model == IntListLikeColumnModel([1, 2, 3, 4])

    with pytest.raises(TypeError):
        a_model - b  # type: ignore[operator]


def test_json_max_level1_column_model_accepts_scalars_dicts_and_lists() -> None:
    data = [1, 'abc', None, {'a': 1, 'b': None}, [2, 'x', False]]
    col_model = JsonMaxLevel1ColumnModel(data)

    assert col_model.content == data
    assert col_model.to_data() == data


def test_json_max_level1_column_model_rejects_nested_list_in_dict() -> None:
    with pytest.raises(ValidationError):
        JsonMaxLevel1ColumnModel([{'a': [1, 2]}])


def test_json_max_level2_column_model_accepts_level2_nested_values() -> None:
    data = [
        1,
        ['x', {
            'k': 2
        }, [3, None]],
        {
            'a': 1,
            'b': {
                'k': 3
            },
            'c': ['y', False, None],
        },
    ]
    col_model = JsonMaxLevel2ColumnModel(data)

    assert col_model.content == data
    assert col_model.to_data() == data


def test_json_max_level2_column_model_rejects_level3_dict_nesting() -> None:
    with pytest.raises(ValidationError):
        JsonMaxLevel2ColumnModel([{'a': {'b': {'c': 1}}}])


def test_json_scalar_column_wise_table_uses_scalar_column_model() -> None:
    data = {
        'a': [1, 2],
        'b': ['x', None],
    }

    table_model = JsonScalarColumnWiseTableWithColNamesModel(data)

    assert table_model.to_data() == data
    assert table_model.col_names == ('a', 'b')
    assert table_model['a'].to_data() == [1, 2]

    assert dict(table_model[0]) == {'a': 1, 'b': 'x'}
    assert dict(table_model[1]) == {'a': 2, 'b': None}

    assert (table_model + table_model).to_data() == {
        'a': [1, 2, 1, 2],
        'b': ['x', None, 'x', None],
    }


def test_json_max_level1_column_wise_table_iterates_rows_and_supports_addition() -> None:
    cell_0_0 = 1
    cell_0_1 = ['x', None]
    cell_1_0 = {'k': 2}
    cell_1_1 = 3
    cell_2_0 = 4
    cell_2_1 = [False]

    data = {
        'a': [cell_0_0, cell_1_0],
        'b': [cell_0_1, cell_1_1],
    }
    other = {
        'a': [cell_2_0],
        'b': [cell_2_1],
    }

    table_model = JsonMaxLevel1ColumnWiseTableWithColNamesModel(data)
    other_table_model = JsonMaxLevel1ColumnWiseTableWithColNamesModel(other)

    assert table_model.to_data() == data
    assert isinstance(table_model['a'], JsonMaxLevel1ColumnModel)

    assert dict(table_model[0]) == {'a': cell_0_0, 'b': cell_0_1}
    assert dict(table_model[1]) == {'a': cell_1_0, 'b': cell_1_1}

    assert (table_model + other_table_model).to_data() == {
        'a': [cell_0_0, cell_1_0, cell_2_0],
        'b': [cell_0_1, cell_1_1, cell_2_1],
    }


def test_json_max_level2_column_wise_table_supports_row_access_iteration_and_addition() -> None:
    cell_0_0 = 1
    cell_0_1 = {'m': 1, 'n': {'p': 2}, 'o': ['u', None]}
    cell_1_0 = ['x', {'k': 2}, [3]]
    cell_1_1 = {'m': 2, 'n': {'p': 3}, 'o': ['v', False]}
    cell_2_0 = None
    cell_2_1 = {'m': 3, 'n': {'p': 4}, 'o': ['w', True]}

    data = {
        'a': [cell_0_0, cell_1_0],
        'b': [cell_0_1, cell_1_1],
    }
    other = {
        'a': [cell_2_0],
        'b': [cell_2_1],
    }

    table_model = JsonMaxLevel2ColumnWiseTableWithColNamesModel(data)
    other_table_model = JsonMaxLevel2ColumnWiseTableWithColNamesModel(other)

    assert table_model.to_data() == data
    assert isinstance(table_model['a'], JsonMaxLevel2ColumnModel)

    assert dict(table_model[0]) == {'a': cell_0_0, 'b': cell_0_1}
    assert dict(table_model[1]) == {'a': cell_1_0, 'b': cell_1_1}

    assert (table_model + other_table_model).to_data() == {
        'a': [cell_0_0, cell_1_0, cell_2_0],
        'b': [cell_0_1, cell_1_1, cell_2_1],
    }
