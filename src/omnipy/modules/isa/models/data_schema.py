# generated by datamodel-codegen:
#   filename:  data_schema.json
#   timestamp: 2024-02-07T08:09:26+00:00

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Field

from . import comment_schema


class FieldType(Enum):
    Data = 'Data'


class Type(Enum):
    Raw_Data_File = 'Raw Data File'
    Derived_Data_File = 'Derived Data File'
    Image_File = 'Image File'
    Acquisition_Parameter_Data_File = 'Acquisition Parameter Data File'
    Derived_Spectral_Data_File = 'Derived Spectral Data File'
    Protein_Assignment_File = 'Protein Assignment File'
    Raw_Spectral_Data_File = 'Raw Spectral Data File'
    Peptide_Assignment_File = 'Peptide Assignment File'
    Array_Data_File = 'Array Data File'
    Derived_Array_Data_File = 'Derived Array Data File'
    Post_Translational_Modification_Assignment_File = (
        'Post Translational Modification Assignment File')
    Derived_Array_Data_Matrix_File = 'Derived Array Data Matrix File'
    Free_Induction_Decay_Data_File = 'Free Induction Decay Data File'
    Metabolite_Assignment_File = 'Metabolite Assignment File'
    Array_Data_Matrix_File = 'Array Data Matrix File'


class IsaDataSchema(BaseModel):
    class Config:
        extra = Extra.forbid

    field_id: Optional[str] = Field(None, alias='@id')
    field_context: Optional[str] = Field(None, alias='@context')
    field_type: Optional[FieldType] = Field(None, alias='@type')
    name: Optional[str] = None
    type: Optional[Type] = None
    comments: Optional[List[comment_schema.IsaCommentSchema]] = None
