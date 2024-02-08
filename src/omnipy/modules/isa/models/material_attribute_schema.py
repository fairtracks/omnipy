# generated by datamodel-codegen:
#   filename:  material_attribute_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Extra, Field

from omnipy.data.model import Model

from . import ontology_annotation_schema


class FieldType(Enum):
    MaterialAttribute = 'MaterialAttribute'


class IsaMaterialAttributeSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    characteristicType: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = None


class IsaMaterialAttributeModel(Model[IsaMaterialAttributeSchema]):
    ...