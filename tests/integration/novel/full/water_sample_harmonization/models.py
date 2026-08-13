from enum import Enum
from typing import cast, Literal, TypeAlias

from omnipy.components.general.models import ConverterModel
from omnipy.components.raw.models import DateModel
from omnipy.components.raw.utils import RegexMatch
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.util import pydantic as pyd

MeasurementType: TypeAlias = Literal['ammonium', 'nitrate', 'phosphorus', 'temperature']


class Unit(str, Enum):
    CELSIUS = 'deg_C'
    MGL = 'mg/L'


class NormalizedMeasurementRecord(pyd.BaseModel):
    class Config:
        use_enum_values = True

    type: MeasurementType
    value: float
    unit: Unit


class NormalizedBatchRecord(pyd.BaseModel):
    sample_key: str
    catchment_id: str
    monitoring_date: DateModel
    location_name: str
    measurements: list[NormalizedMeasurementRecord]


class NormalizedBatchesDataset(Dataset[Model[list[NormalizedBatchRecord]]]):
    ...


class RiverMeasurementRecord(pyd.BaseModel):
    name: str


class RiverTempMeasurementRecord(RiverMeasurementRecord):
    value_celsius: float


class RiverMgConcMeasurementRecord(RiverMeasurementRecord):
    value_mg_l: float


class RiverUgConcMeasurementRecord(RiverMeasurementRecord):
    value_ug_l: float


RiverMeasurementRecordType: TypeAlias = (
    RiverTempMeasurementRecord | RiverMgConcMeasurementRecord | RiverUgConcMeasurementRecord)


class RiverBatchRecord(pyd.BaseModel):
    river_batch_id: str
    catchment: str
    sampled_at: str
    station: str
    sample_alias: str
    measurements: list[RiverMeasurementRecordType]


class WastewaterMeasurementRecord(pyd.BaseModel):
    metric: str
    value: float
    unit: str


class WastewaterBatchRecord(pyd.BaseModel):
    wastewater_batch_id: str
    catchment_code: str
    monitoring_date: str
    treatment_plant: str
    sample_alias: str
    measurements: list[WastewaterMeasurementRecord]


class MeasurementTypeMapper(ConverterModel[str, MeasurementType]):
    @classmethod
    def _convert(cls, data: str) -> MeasurementType:
        match data:
            case 'ammon':
                return 'ammonium'
            case 'phosph':
                return 'phosphorus'
            case _:
                return cast(MeasurementType, data.lower())


class NormalizedRiverMeasurementMapper(ConverterModel[
        RiverMeasurementRecordType,
        NormalizedMeasurementRecord,
]):
    @classmethod
    def _convert(cls, data: RiverMeasurementRecordType) -> NormalizedMeasurementRecord:
        match data:
            case RiverMgConcMeasurementRecord():
                return NormalizedMeasurementRecord(
                    type=MeasurementTypeMapper.convert(data.name),
                    value=data.value_mg_l,
                    unit=Unit.MGL,
                )
            case RiverUgConcMeasurementRecord():
                return NormalizedMeasurementRecord(
                    type=MeasurementTypeMapper.convert(data.name),
                    value=data.value_ug_l / 1000,
                    unit=Unit.MGL,
                )
            case RiverTempMeasurementRecord():
                return NormalizedMeasurementRecord(
                    type=MeasurementTypeMapper.convert(data.name),
                    value=data.value_celsius,
                    unit=Unit.CELSIUS,
                )


class NormalizedRiverBatchRecordMapper(ConverterModel[
        RiverBatchRecord,
        NormalizedBatchRecord,
]):
    @classmethod
    def _convert(cls, data: RiverBatchRecord) -> NormalizedBatchRecord:
        return NormalizedBatchRecord(
            sample_key=data.sample_alias.lower(),
            catchment_id=data.catchment,
            monitoring_date=DateModel(data.sampled_at),
            location_name=data.station,
            measurements=list(NormalizedRiverMeasurementMapper.convert_all(data.measurements)),
        )


class UnitMapper(ConverterModel[str, Unit]):
    @classmethod
    def _convert(cls, data: str) -> Unit:
        match RegexMatch(data.lower()):
            case r'deg.?c':
                return Unit.CELSIUS
            case r'mg.?l':
                return Unit.MGL
            case _:
                raise ValueError(f'Invalid unit: {data}')


class NormalizedWastewaterMeasurementMapper(ConverterModel[
        WastewaterMeasurementRecord,
        NormalizedMeasurementRecord,
]):
    @classmethod
    def _convert(cls, data: WastewaterMeasurementRecord) -> NormalizedMeasurementRecord:
        return NormalizedMeasurementRecord(
            type=MeasurementTypeMapper.convert(data.metric),
            value=data.value,
            unit=UnitMapper.convert(data.unit),
        )


class NormalizedWastewaterBatchRecordMapper(ConverterModel[
        WastewaterBatchRecord,
        NormalizedBatchRecord,
]):
    @classmethod
    def _convert(cls, data: WastewaterBatchRecord) -> NormalizedBatchRecord:
        return NormalizedBatchRecord(
            sample_key=data.sample_alias.lower(),
            catchment_id=data.catchment_code,
            monitoring_date=DateModel(data.monitoring_date),
            location_name=data.treatment_plant,
            measurements=list(NormalizedWastewaterMeasurementMapper.convert_all(data.measurements)),
        )
