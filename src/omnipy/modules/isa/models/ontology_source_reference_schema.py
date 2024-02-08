# generated by datamodel-codegen:
#   filename:  ontology_source_reference_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from omnipy.data.model import Model

from . import comment_schema


class FieldType(Enum):
    OntologySourceReference = 'OntologySourceReference'


class IsaOntologySourceReferenceSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    comments: Optional[List[comment_schema.IsaCommentModel]] = None
    description: Optional[str] = None
    file: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None


class IsaOntologySourceReferenceModel(Model[IsaOntologySourceReferenceSchema]):
    ...
