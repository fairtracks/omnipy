from dataclasses import dataclass
from typing import Generic, TypeVar

from omnipy.shared.protocols.compute.job import IsAnyFlowTemplate

_ArgT = TypeVar('_ArgT')
_ReturnT = TypeVar('_ReturnT')


@dataclass
class FlowCase(Generic[_ArgT, _ReturnT]):
    """Define FlowCase."""
    name: str
    flow_template: IsAnyFlowTemplate
