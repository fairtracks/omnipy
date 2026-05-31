from omnipy.components.tables.models import (JsonScalarColumnWiseTableWithColNamesModel,
                                             PrintableTable)
from omnipy.data.model import Model
import omnipy.util.pydantic as pyd

from ..models.investigation_schema import IsaInvestigationModel, IsaInvestigationSchema

ISA_JSON_MODEL_TOP_LEVEL_KEY: str = 'investigation'


class IsaTopLevelSchema(pyd.BaseModel):
    """Pydantic schema for the top-level ISA investigation wrapper."""

    class Config:
        """Pydantic configuration for strict ISA top-level validation."""

        extra = pyd.Extra.forbid
        use_enum_values = True

    investigation: IsaInvestigationModel | None = None


class IsaTopLevelModel(Model[IsaTopLevelSchema]):
    """ISA model representing the top-level investigation wrapper."""

    ...


class IsaJsonModel(Model[IsaInvestigationSchema | IsaTopLevelModel]):
    """ISA JSON model accepting investigation or top-level wrapper input."""

    class Config:
        """Pydantic configuration for ISA JSON union parsing."""

        smart_union = False

    @classmethod
    def _parse_data(cls, data: IsaInvestigationSchema | IsaTopLevelModel) -> IsaTopLevelModel:
        if isinstance(data, IsaTopLevelModel):
            return data
        else:
            return IsaTopLevelModel(investigation=data)


class FlattenedIsaJsonModel(Model[JsonScalarColumnWiseTableWithColNamesModel], PrintableTable):
    ...
