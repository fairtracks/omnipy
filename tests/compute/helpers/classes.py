from typing import NamedTuple, Type

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


class FlowClsTuple(NamedTuple):
    template_cls: Type
    flow_cls: Type


class CustomStrModel(Model[str]):
    ...


class CustomStrDataset(Dataset[CustomStrModel]):
    ...
