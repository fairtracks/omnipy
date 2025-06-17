from __future__ import annotations
from typing import Any, Dict, List

from pydantic import root_validator
from omnipy.data.model import Model


class ROCrate(Model[Dict[str, Any]]):
    @root_validator(pre=True)
    def _basic_checks(cls, data):
        root = data.get("__root__", data)
        if root.get("@context") != "https://w3id.org/ro/crate/1.1/context":
            raise ValueError("RO-Crate requires the 1.1 context")
        if not isinstance(root.get("@graph"), list):
            raise ValueError("@graph must be a list")
        return data
