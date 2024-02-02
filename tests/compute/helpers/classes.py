from typing import NamedTuple, Type

from omnipy import Dataset, Model


class FlowClsTuple(NamedTuple):
    template_cls: Type
    flow_cls: Type


class CustomStrModel(Model[str]):
    ...


class CustomStrDataset(Dataset[CustomStrModel]):
    ...
