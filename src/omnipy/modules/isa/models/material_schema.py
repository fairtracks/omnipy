#   filename:  material_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from omnipy.data.model import Model

from . import comment_schema, material_attribute_value_schema


class FieldType(Enum):
    Material = 'Material'


class Type(Enum):
    Extract_Name = 'Extract Name'
    Labeled_Extract_Name = 'Labeled Extract Name'


class IsaMaterialSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    name: Optional[str] = None
    type: Optional[Type] = None
    characteristics: Optional[List[
        material_attribute_value_schema.IsaMaterialAttributeValueModel]] = None
    derivesFrom: Optional[List['IsaMaterialModel']] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaMaterialModel(Model[IsaMaterialSchema]):
    ...


IsaMaterialSchema.update_forward_refs()
