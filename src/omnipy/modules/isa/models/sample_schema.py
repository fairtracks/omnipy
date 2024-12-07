# generated by datamodel-codegen:
#   filename:  sample_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from . import comment_schema, factor_value_schema, material_attribute_value_schema, source_schema


class FieldType(Enum):
    Sample = 'Sample'


class IsaSampleSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    name: Optional[str] = None
    characteristics: Optional[List[
        material_attribute_value_schema.IsaMaterialAttributeValueModel]] = None
    factorValues: Optional[List[factor_value_schema.IsaFactorValueModel]] = None
    derivesFrom: Optional[List[source_schema.IsaSourceModel]] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaSampleModel(Model[IsaSampleSchema]):
    ...
