# generated by datamodel-codegen:
#   filename:  study_group.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

from . import comment_schema, factor_value_schema, sample_schema


class FieldType(Enum):
    Study_Group = 'Study Group'


class IsaStudyGroupSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    name: Optional[str] = None
    factor_levels: Optional[List[factor_value_schema.IsaFactorValueModel]] = None
    study_group_size: Optional[int] = None
    members: Optional[List[sample_schema.IsaSampleModel]] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaStudyGroupModel(Model[IsaStudyGroupSchema]):
    ...
