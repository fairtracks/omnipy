# generated by datamodel-codegen:
#   filename:  factor_value_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional, Union

from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from . import comment_schema, factor_schema, ontology_annotation_schema


class FieldType(Enum):
    FactorValue = 'FactorValue'


class IsaFactorValueSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    category: Optional[factor_schema.IsaFactorModel] = None
    value: Optional[Union[ontology_annotation_schema.IsaOntologyReferenceModel, str, float]] = None
    unit: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaFactorValueModel(Model[IsaFactorValueSchema]):
    ...
