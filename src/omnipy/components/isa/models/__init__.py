from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

from ...json.models import JsonListOfDictsOfScalarsModel
from ..models.investigation_schema import IsaInvestigationModel, IsaInvestigationSchema

ISA_JSON_MODEL_TOP_LEVEL_KEY: str = 'investigation'


class IsaTopLevelSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    investigation: IsaInvestigationModel | None = None


class IsaTopLevelModel(Model[IsaTopLevelSchema]):
    ...


class IsaJsonModel(Model[IsaInvestigationSchema | IsaTopLevelModel]):
    class Config:
        smart_union = False

    @classmethod
    def _parse_data(cls, data: IsaInvestigationSchema | IsaTopLevelModel) -> IsaTopLevelModel:
        if isinstance(data, IsaTopLevelModel):
            return data
        else:
            return IsaTopLevelModel(investigation=data)


class FlattenedIsaJsonModel(Model[JsonListOfDictsOfScalarsModel]):
    ...
