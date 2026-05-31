from omnipy.components.tables.models import (JsonScalarColumnWiseTableWithColNamesModel,
                                             PrintableTable)
from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from ..models.investigation_schema import IsaInvestigationModel, IsaInvestigationSchema

ISA_JSON_MODEL_TOP_LEVEL_KEY: str = 'investigation'


class IsaTopLevelSchema(pyd.BaseModel):
    """Schema for top-level ISA-JSON documents.

    This schema reflects the common envelope where an ISA investigation is
    stored below the ``investigation`` key.

    Attributes:
        investigation: Wrapped investigation payload when present.
    """

    class Config:
        """Pydantic settings for top-level ISA validation.

        Attributes:
            extra: Forbids keys that are not part of the schema.
            use_enum_values: Serializes enum instances as their value strings.
        """

        extra = pyd.Extra.forbid
        use_enum_values = True

    investigation: IsaInvestigationModel | None = None


class IsaTopLevelModel(Model[IsaTopLevelSchema]):
    """Omnipy model wrapper for :class:`IsaTopLevelSchema`.

    The wrapper provides Omnipy ``Model`` behavior while preserving the
    top-level ISA-JSON document shape.
    """

    ...


class IsaJsonModel(Model[IsaInvestigationSchema | IsaTopLevelModel]):
    """Union model that accepts both common ISA investigation shapes.

    Input can be either a raw :class:`IsaInvestigationSchema` object or a
    top-level wrapper containing the ``investigation`` field.
    """

    class Config:
        """Pydantic settings for ISA union parsing behavior.

        Attributes:
            smart_union: Keeps explicit branch resolution for union parsing.
        """

        smart_union = False

    @classmethod
    def _parse_data(cls, data: IsaInvestigationSchema | IsaTopLevelModel) -> IsaTopLevelModel:
        if isinstance(data, IsaTopLevelModel):
            return data
        else:
            return IsaTopLevelModel(investigation=data)


class FlattenedIsaJsonModel(Model[JsonScalarColumnWiseTableWithColNamesModel], PrintableTable):
    ...
