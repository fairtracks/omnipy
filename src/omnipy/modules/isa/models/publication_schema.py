# generated by datamodel-codegen:
#   filename:  publication_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from omnipy.data.model import Model

from . import comment_schema, ontology_annotation_schema


class FieldType(Enum):
    Publication = 'Publication'


class IsaPublicationSchema(BaseModel):
    class Config:
        extra = Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    pubMedID: Optional[str] = None
    doi: Optional[str] = None
    authorList: Optional[str] = None
    title: Optional[str] = None
    status: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaPublicationModel(Model[IsaPublicationSchema]):
    ...
