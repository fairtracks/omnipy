# generated by datamodel-codegen:
#   filename:  study_group.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from . import comment_schema, factor_value_schema, sample_schema


class FieldType(Enum):
    Study_Group = 'Study Group'


class IsaStudyGroupSchema(BaseModel):
    class Config:
        extra = Extra.forbid

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    name: Optional[str] = None
    factor_levels: Optional[List[factor_value_schema.IsaFactorValueSchema]] = None
    study_group_size: Optional[int] = None
    members: Optional[List[sample_schema.IsaSampleSchema]] = None
    comments: Optional[List[comment_schema.IsaCommentSchema]] = None
