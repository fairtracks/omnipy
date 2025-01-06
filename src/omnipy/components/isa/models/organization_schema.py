# generated by datamodel-codegen:
#   filename:  organization_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import Optional

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd


class FieldType(Enum):
    Organization = 'Organization'


class IsaOrganizationSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    name: Optional[str] = None


class IsaOrganizationModel(Model[IsaOrganizationSchema]):
    ...
