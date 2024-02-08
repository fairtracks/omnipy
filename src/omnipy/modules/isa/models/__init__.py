from pydantic import BaseModel, Extra

from omnipy.data.model import Model
from omnipy.modules.isa.models.investigation_schema import (IsaInvestigationModel,
                                                            IsaInvestigationSchema)
from omnipy.modules.json.models import JsonListOfDictsOfScalarsModel

ISA_JSON_MODEL_TOP_LEVEL_KEY: str = 'investigation'


class IsaTopLevelSchema(BaseModel):
    class Config:
        extra = Extra.forbid
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
