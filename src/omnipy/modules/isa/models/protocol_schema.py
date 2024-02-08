# generated by datamodel-codegen:
#   filename:  protocol_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from omnipy.data.model import Model

from . import comment_schema, ontology_annotation_schema, protocol_parameter_schema


class Component(BaseModel):
    componentName: Optional[str] = None
    componentType: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = (None)
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class FieldType(Enum):
    Protocol = 'Protocol'


class IsaProtocolSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    name: Optional[str] = None
    protocolType: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = None
    description: Optional[str] = None
    uri: Optional[str] = None
    version: Optional[str] = None
    parameters: Optional[List[protocol_parameter_schema.IsaProtocolParameterModel]] = (None)
    components: Optional[List[Component]] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaProtocolModel(Model[IsaProtocolSchema]):
    ...