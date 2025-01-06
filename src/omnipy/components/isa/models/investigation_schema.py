# generated by datamodel-codegen:
#   filename:  investigation_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

from . import (comment_schema,
               ontology_source_reference_schema,
               person_schema,
               publication_schema,
               study_schema)
from .validators import date_to_iso_format


class FieldType(Enum):
    Investigation = 'Investigation'


class IsaInvestigationSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    filename: Optional[str] = None
    identifier: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    submissionDate: Optional[Union[datetime, date, pyd.constr(max_length=0)]] = None
    publicReleaseDate: Optional[Union[datetime, date, pyd.constr(max_length=0)]] = None
    ontologySourceReferences: Optional[List[
        ontology_source_reference_schema.IsaOntologySourceReferenceModel]] = None
    publications: Optional[List[publication_schema.IsaPublicationModel]] = None
    people: Optional[List[person_schema.IsaPersonModel]] = None
    studies: Optional[List[study_schema.IsaStudyModel]] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None

    _date_to_iso_format = pyd.validator(
        'submissionDate', 'publicReleaseDate', allow_reuse=True)(
            date_to_iso_format)


class IsaInvestigationModel(Model[IsaInvestigationSchema]):
    ...
