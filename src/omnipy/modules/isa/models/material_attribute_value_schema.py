# generated by datamodel-codegen:
#   filename:  material_attribute_value_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional, Union

from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from . import comment_schema, material_attribute_schema, ontology_annotation_schema


class FieldType(Enum):
    MaterialAttributeValue = 'MaterialAttributeValue'


class IsaMaterialAttributeValueSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    category: Optional[material_attribute_schema.IsaMaterialAttributeModel] = None
    value: Optional[Union[ontology_annotation_schema.IsaOntologyReferenceModel, str, float]] = None
    unit: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaMaterialAttributeValueModel(Model[IsaMaterialAttributeValueSchema]):
    ...
