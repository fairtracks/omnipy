# generated by datamodel-codegen:
#   filename:  ontology_annotation_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Extra, Field

from . import comment_schema


class FieldType(Enum):
    OntologyAnnotation = 'OntologyAnnotation'


class IsaOntologyReferenceSchema(BaseModel):
    class Config:
        extra = Extra.forbid

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    annotationValue: Optional[Union[str, float]] = None
    termSource: Optional[str] = Field(
        None,
        description=
        'The abbreviated ontology name. It should correspond to one of the sources as specified in the ontologySourceReference section of the Investigation.',
    )
    termAccession: Optional[str] = None
    comments: Optional[List[comment_schema.IsaCommentSchema]] = None
