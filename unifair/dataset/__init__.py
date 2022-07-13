from abc import ABC, abstractmethod
from collections import UserDict
from typing import Any

from pydantic import BaseModel, validate_model


class OldDataset(ABC, UserDict, BaseModel):
    def __init__(self):
        BaseModel.__init__(self, data={})
        UserDict.__init__(self, {})

    @abstractmethod
    def __setitem__(self, obj_type: str, data_obj: Any) -> None:
        pass


def validate(model: BaseModel):
    *_, validation_error = validate_model(model.__class__, model.__dict__)
    if validation_error:
        raise validation_error
