from pydantic import BaseModel, ValidationError
import pytest

from omnipy.modules.tables.models import PydanticRecordModel, TableOfPydanticRecordsModel


def test_pydantic_record_model_all_required() -> None:
    class NameRecord(BaseModel):
        firstname: str
        lastname: str

    class NameRecordModel(PydanticRecordModel[NameRecord]):
        pass

    record = NameRecordModel(firstname='John', lastname='Doe')
    assert record.contents == NameRecord(firstname='John', lastname='Doe')
    assert record.to_data() == {'firstname': 'John', 'lastname': 'Doe'}

    record = NameRecordModel({'firstname': 'Jane', 'lastname': 'Doe'})
    assert record.contents == NameRecord(firstname='Jane', lastname='Doe')
    assert record.to_data() == {'firstname': 'Jane', 'lastname': 'Doe'}

    record = NameRecordModel(NameRecord(firstname='Robert', lastname='Doe'))
    assert record.contents == NameRecord(firstname='Robert', lastname='Doe')
    assert record.to_data() == {'firstname': 'Robert', 'lastname': 'Doe'}

    record = NameRecordModel(['Emily', 'Doe'])
    assert record.contents == NameRecord(firstname='Emily', lastname='Doe')
    assert record.to_data() == {'firstname': 'Emily', 'lastname': 'Doe'}

    with pytest.raises(ValidationError):
        NameRecordModel(firstname='Tarzan')


def test_pydantic_record_model_optional() -> None:
    class NameRecordOptionalLastName(BaseModel):
        firstname: str
        lastname: str | None = None

    class NameRecordOptionalLastNameModel(PydanticRecordModel[NameRecordOptionalLastName]):
        pass

    record = NameRecordOptionalLastNameModel(firstname='Tarzan')
    assert record.contents == NameRecordOptionalLastName(firstname='Tarzan')
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None}

    record = NameRecordOptionalLastNameModel(['Tarzan', None])
    assert record.contents == NameRecordOptionalLastName(firstname='Tarzan')
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None}

    NameRecordOptionalLastNameModel(firstname='Tarzan', title='King of Apes')
    assert record.contents == NameRecordOptionalLastName(firstname='Tarzan')
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None}


def test_pydantic_record_model_extra_fields_config() -> None:
    class NameRecordNoExtraFields(BaseModel):
        firstname: str
        lastname: str | None = None

        class Config:
            extra = 'forbid'

    class NameRecordNoExtraFieldsModel(PydanticRecordModel[NameRecordNoExtraFields]):
        pass

    with pytest.raises(ValidationError):
        NameRecordNoExtraFieldsModel(firstname='Tarzan', title='King of Apes')

    class NameRecordExtraFields(BaseModel):
        firstname: str
        lastname: str | None = None

        class Config:
            extra = 'allow'

    class NameRecordExtraFieldsModel(PydanticRecordModel[NameRecordExtraFields]):
        pass

    record = NameRecordExtraFieldsModel(firstname='Tarzan', title='King of Apes')
    assert record.contents == NameRecordExtraFields(
        firstname='Tarzan',  # type: ignore[call-arg]
        title='King of Apes',
    )
    assert record.to_data() == {'firstname': 'Tarzan', 'lastname': None, 'title': 'King of Apes'}


def test_table_of_pydantic_records_model_from_list_of_dicts() -> None:
    class NameRecord(BaseModel):
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

    assert len(table.contents) == 2
    assert isinstance(table.contents[0], PydanticRecordModel)
    assert isinstance(table.contents[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


def test_table_of_pydantic_records_model_from_list_of_lists() -> None:
    class NameRecord(BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    table = TableOfNameRecordsModel([
        ['John', 'Doe'],
        ['Jane', 'Doe'],
    ])

    assert len(table.contents) == 2
    assert isinstance(table.contents[0], PydanticRecordModel)
    assert isinstance(table.contents[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]


def test_table_of_pydantic_records_model_from_str() -> None:
    class NameRecord(BaseModel):
        firstname: str
        lastname: str

    class TableOfNameRecordsModel(TableOfPydanticRecordsModel[NameRecord]):
        pass

    table = TableOfNameRecordsModel("John\tDoe\nJane\tDoe")

    assert len(table.contents) == 2
    assert isinstance(table.contents[0], PydanticRecordModel)
    assert isinstance(table.contents[1], PydanticRecordModel)

    assert table.to_data() == [
        {
            'firstname': 'John', 'lastname': 'Doe'
        },
        {
            'firstname': 'Jane', 'lastname': 'Doe'
        },
    ]
