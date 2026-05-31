#   filename:  material_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

"""ISA model representing a material in an investigation."""

from enum import Enum
from typing import List, Optional

from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from . import comment_schema, material_attribute_value_schema


class FieldType(Enum):
    """JSON-LD type labels used for ISA material entities.

    Attributes:
        Material: Marks a JSON object as an ISA material.
    """

    Material = 'Material'


class Type(Enum):
    """Allowed ISA material category labels.

    Attributes:
        Extract_Name: Label for an extract material.
        Labeled_Extract_Name: Label for a labeled extract material.
    """

    Extract_Name = 'Extract Name'
    Labeled_Extract_Name = 'Labeled Extract Name'


class IsaMaterialSchema(pyd.BaseModel):
    """Schema for non-sample materials in ISA studies.

    Attributes:
        name: Material name or identifier.
        type: Controlled label for material category.
        characteristics: Assigned material attribute values.
        derivesFrom: Parent materials from which this material was derived.
        comments: Optional comments attached to the material.
    """

    class Config:
        """Validation settings for ISA material schema parsing.

        Attributes:
            extra: Rejects unknown fields.
            use_enum_values: Serializes enum fields by raw values.
        """

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
    """Omnipy model wrapper for ISA material records.

    Provides Omnipy model semantics on top of
    :class:`IsaMaterialSchema` validation.
    """

    ...


IsaMaterialSchema.update_forward_refs()
