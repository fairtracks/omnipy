# src/omnipy/components/rocrate/models.py
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, root_validator
from omnipy.data.model import Model


class Thing(BaseModel):
    id: str = ...
    type: str = ...
    name: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        fields = {"id": "@id", "type": "@type"}


class Dataset(Thing):
    type: Literal["Dataset"] = "Dataset"
    hasPart: Optional[List[Dict[str, str]]] = None


class File(Thing):
    type: Literal["File"] = "File"
    encodingFormat: Optional[str] = None
    contentSize: Optional[str] = None
    description: Optional[str] = None


Entity = Dataset | File | Thing


class ROCrate(Model[Dict[str, Any]]):
    @root_validator(pre=True)
    def _basic_checks(cls, values):
        crate = values.get("__root__", values)
        if crate.get("@context") != "https://w3id.org/ro/crate/1.1/context":
            raise ValueError("RO-Crate requires the 1.1 context")
        if not isinstance(crate.get("@graph"), list):
            raise ValueError("@graph must be a list")
        return values
