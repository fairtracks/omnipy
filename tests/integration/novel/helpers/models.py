from typing import Dict, Generic, List, Type, TypeVar, Union

from pydantic import BaseConfig, BaseModel, create_model, Extra

from unifair.data.model import Model

# Types

RecordT = TypeVar('RecordT', bound=Model)

RecordSchemaDefType = Dict[str, Type]

# Models


class RecordSchemaDef(Model[RecordSchemaDefType]):
    ...


class RecordSchema(BaseModel):
    ...


def record_schema_factory(data_file: str,
                          record_schema_def: RecordSchemaDefType) -> Type[RecordSchema]:
    class Config(BaseConfig):
        extra = Extra.forbid

    return create_model(
        data_file,
        **dict(((key, (val, val())) for key, val in record_schema_def.items())),
        __config__=Config)


MyRecordSchema = record_schema_factory('MyRecordSchema', {'a': int, 'b': str})

MyOtherRecordSchema = record_schema_factory('MyOtherRecordSchema', {'b': str, 'c': int})


class TableTemplate(Model[List[RecordT]], Generic[RecordT]):
    """This is a generic template model for tables"""


class GeneralRecord(Model[Dict[str, Union[int, str]]]):
    """This is a general record"""


class GeneralTable(Model[TableTemplate[GeneralRecord]]):
    """This is a general table"""
