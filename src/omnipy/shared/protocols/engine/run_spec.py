"""Protocols for engine-facing run-spec adapters."""

from datetime import datetime
import inspect
from inspect import BoundArguments
from logging import INFO
from types import MappingProxyType
from typing import Callable, Protocol, runtime_checkable

from omnipy.shared.protocols.compute.job import ChildJobTemplateLike, IsFuncArgJob
from omnipy.shared.protocols.compute.mixins import IsNestedContext
from omnipy.shared.protocols.hub.log import CanLog
from omnipy.util.callable_types import CallableType


@runtime_checkable
class IsJobRunSpec(CanLog, Protocol):
    """Engine-facing metadata and callable adapter for one job execution."""
    @property
    def name(self) -> str:
        ...

    @property
    def unique_name(self) -> str:
        ...

    @property
    def unique_run_slug(self) -> str:
        ...

    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
        ...

    @property
    def return_type(self) -> type:
        ...

    @property
    def callable_type(self) -> CallableType.Literals:
        ...

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None) -> None:
        ...

    def create_default_run_callable(self) -> Callable:
        ...


@runtime_checkable
class IsTaskRunSpec(IsJobRunSpec, Protocol):
    """Run-spec protocol for applied tasks."""
    @property
    def in_flow_context(self) -> bool:
        ...


@runtime_checkable
class IsFlowRunSpec(IsJobRunSpec, Protocol):
    """Run-spec protocol for applied flows."""
    @property
    def flow_context(self) -> IsNestedContext:
        ...

    def get_bound_args(self, *args: object, **kwargs: object) -> BoundArguments:
        ...


@runtime_checkable
class IsChildJobListArgFlowRunSpec(IsFlowRunSpec, Protocol):
    """Run-spec protocol for flows defined by ordered child-job templates."""
    @property
    def child_job_templates(self) -> tuple[ChildJobTemplateLike, ...]:
        ...


@runtime_checkable
class IsLinearFlowRunSpec(IsChildJobListArgFlowRunSpec, Protocol):
    """Protocol variant of ``LinearFlowRunSpec``."""


@runtime_checkable
class IsDagFlowRunSpec(IsChildJobListArgFlowRunSpec, Protocol):
    """Protocol variant of ``DagFlowRunSpec``."""


@runtime_checkable
class IsFuncFlowRunSpec(IsFlowRunSpec, Protocol):
    """Protocol variant of ``FuncFlowRunSpec``."""


class IsJobRunSpecFactory(Protocol):
    """Constructor protocol for run-spec classes selected by job type."""
    def __call__(self, job: IsFuncArgJob, run_callable: Callable) -> IsJobRunSpec:
        ...
