#   filename:  material_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

"""ISA model representing a material in an investigation."""

from enum import Enum
from typing import List, Optional

from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from . import comment_schema, material_attribute_value_schema


class FieldType(Enum):
    """Enum of JSON-LD type labels for ISA materials."""

    Material = 'Material'


class Type(Enum):
    """Enum of ISA material categories."""

    Extract_Name = 'Extract Name'
    Labeled_Extract_Name = 'Labeled Extract Name'


class IsaMaterialSchema(pyd.BaseModel):
    """Pydantic schema for a non-sample material in a study."""

    class Config:
        """Pydantic configuration for strict ISA material validation."""

        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    name: Optional[str] = None
    type: Optional[Type] = None
    characteristics: Optional[List[
        material_attribute_value_schema.IsaMaterialAttributeValueModel]] = None
    derivesFrom: Optional[List['IsaMaterialModel']] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaMaterialModel(Model[IsaMaterialSchema]):
    """ISA model representing a non-sample material in a study."""

    ...


IsaMaterialSchema.update_forward_refs()
