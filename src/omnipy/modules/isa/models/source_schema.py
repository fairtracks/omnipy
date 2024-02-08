# generated by datamodel-codegen:
#   filename:  source_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from omnipy.data.model import Model

from . import comment_schema, material_attribute_value_schema


class FieldType(Enum):
    Source = 'Source'


class IsaSourceSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        use_enum_values = True
        use_enum_values = True

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    name: Optional[str] = None
    characteristics: Optional[List[
        material_attribute_value_schema.IsaMaterialAttributeValueModel]] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaSourceModel(Model[IsaSourceSchema]):
    ...