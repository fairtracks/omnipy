# generated by datamodel-codegen:
#   filename:  assay_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

from . import (comment_schema,
               data_schema,
               material_attribute_schema,
               material_schema,
               ontology_annotation_schema,
               process_schema,
               sample_schema)


class FieldType(Enum):
    Assay = 'Assay'


class _Materials(pyd.BaseModel):
    samples: Optional[List[sample_schema.IsaSampleModel]] = None
    otherMaterials: Optional[List[material_schema.IsaMaterialModel]] = None


class _MaterialsModel(Model[_Materials]):
    ...


class IsaAssayJsonSchema(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.forbid
        use_enum_values = True

    field_id: Optional[str] = pyd.Field(None, alias='@id')
    field_context: Optional[str] = pyd.Field(None, alias='@context')
    field_type: Optional[FieldType] = pyd.Field(None, alias='@type')
    filename: Optional[str] = None
    measurementType: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = (None)
    technologyType: Optional[ontology_annotation_schema.IsaOntologyReferenceModel] = (None)
    technologyPlatform: Optional[str] = None
    dataFiles: Optional[List[data_schema.IsaDataModel]] = None
    materials: Optional[_MaterialsModel] = None
    characteristicCategories: Optional[List[material_attribute_schema.IsaMaterialAttributeModel]] =\
        pyd.Field(
            None,
            description='List of all the characteristics categories (or material attributes) '
            'defined in the study, used to avoid duplication of their declaration '
            'when each material_attribute_value is created. ')
    unitCategories: Optional[List[ontology_annotation_schema.IsaOntologyReferenceModel]] = \
        pyd.Field(
            None,
            description='List of all the unitsdefined in the study, used to avoid duplication '
                        'of their declaration when each value is created. ')
    processSequence: Optional[List[process_schema.IsaProcessOrProtocolApplicationModel]] = None
    comments: Optional[List[comment_schema.IsaCommentModel]] = None


class IsaAssayJsonModel(Model[IsaAssayJsonSchema]):
    ...
