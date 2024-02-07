# generated by datamodel-codegen:
#   filename:  person_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Extra, Field

from . import comment_schema, ontology_annotation_schema


class FieldType(Enum):
    Person = 'Person'


class IsaPersonSchema(BaseModel):
    class Config:
        extra = Extra.forbid

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    midInitials: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    address: Optional[str] = None
    affiliation: Optional[str] = None
    roles: Optional[List[ontology_annotation_schema.IsaOntologyReferenceSchema]] = None
    comments: Optional[List[comment_schema.IsaCommentSchema]] = None
