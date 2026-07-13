"""Top-level task and flow protocol definitions."""

from datetime import datetime
import inspect
import os
from textwrap import dedent
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, ParamSpec, Protocol, runtime_checkable, TypeVar

from omnipy.shared._typedefs import _JobT, _JobTemplateT
from omnipy.shared.enums.job import (OutputStorageProtocolOptions,
                                     PersistOutputsOptions,
                                     RestoreOutputsOptions)
from omnipy.shared.protocols.compute.job_creator import IsJobCreator
from omnipy.shared.protocols.compute.mixins import IsNestedContext, IsUniquelyNamedJob
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.log import CanLog
from omnipy.shared.typedefs import GeneralDecorator
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import is_package_editable

_CallP = ParamSpec('_CallP')
_RetT = TypeVar('_RetT')
_RetCovT = TypeVar('_RetCovT', covariant=True)
_RetContraT = TypeVar('_RetContraT', contravariant=True)

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISJOBBASE_CONFIG_SUMMARY'] = (
        'Return the job configuration visible to this instance.')
    os.environ['OMNIPY_MACRO_ISJOBBASE_CONFIG_DETAILS'] = dedent("""\
        Returns:
            IsJobConfig: Active job configuration used for runtime behavior.
    """)

    os.environ['OMNIPY_MACRO_ISJOBBASE_ENGINE_SUMMARY'] = (
        'Return the engine associated with this job, if any.')
    os.environ['OMNIPY_MACRO_ISJOBBASE_ENGINE_DETAILS'] = dedent("""\
        Returns:
            IsEngine | None: Engine used for decoration and execution, or ``None``.
    """)

    os.environ['OMNIPY_MACRO_ISJOBBASE_IN_FLOW_CONTEXT_SUMMARY'] = (
        'Return whether the job is currently executing inside a flow context.')
    os.environ['OMNIPY_MACRO_ISJOBBASE_IN_FLOW_CONTEXT_DETAILS'] = dedent("""\
        Returns:
            bool: ``True`` when a surrounding flow context is active.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_RETURN_TYPE_SUMMARY'] = (
        'Return the annotated return type of the job callable.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_RETURN_TYPE_DETAILS'] = dedent("""\
        Returns:
            type: Return annotation for the callable.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_ITERATE_OVER_DATA_FILES_SUMMARY'] = (
        'Return whether the job should iterate over dataset items automatically.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_ITERATE_OVER_DATA_FILES_DETAILS'] = dedent("""\
        Returns:
            bool: ``True`` when the first dataset argument is expanded item-by-item.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_DATASET_PARAM_SUMMARY'] = (
        'Return the parameter name used for an explicit output dataset, if any.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_DATASET_PARAM_DETAILS'] = dedent("""\
        Returns:
            str | None: Output-dataset parameter name, or ``None`` when not configured.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_DATASET_CLS_SUMMARY'] = (
        'Return the dataset class used for iterated outputs, if configured.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_DATASET_CLS_DETAILS'] = dedent("""\
        Returns:
            type[IsDataset] | None: Output dataset type, or ``None`` when inferred.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_AUTO_ASYNC_SUMMARY'] = (
        'Return whether coroutine jobs should auto-run outside flow contexts.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_AUTO_ASYNC_DETAILS'] = dedent("""\
        Returns:
            bool: ``True`` when coroutine jobs are automatically awaited or scheduled.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_PERSIST_OUTPUTS_SUMMARY'] = (
        'Return the configured per-job output-persistence preference.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_PERSIST_OUTPUTS_DETAILS'] = dedent("""\
        Returns:
            PersistOutputsOptions.Literals: Persistence setting before config fallback.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_RESTORE_OUTPUTS_SUMMARY'] = (
        'Return the configured per-job output-restore preference.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_RESTORE_OUTPUTS_DETAILS'] = dedent("""\
        Returns:
            RestoreOutputsOptions.Literals: Restore setting before config fallback.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_SUMMARY'] = (
        'Return the configured output-storage protocol preference.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_DETAILS'] = dedent("""\
        Returns:
            OutputStorageProtocolOptions.Literals: Storage-protocol setting before
                config fallback.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_WILL_PERSIST_OUTPUTS_SUMMARY'] = (
        'Return the resolved output-persistence behavior for this run.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_WILL_PERSIST_OUTPUTS_DETAILS'] = dedent("""\
        Returns:
            PersistOutputsOptions.Literals: Effective persistence behavior after
                applying config-following rules.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_WILL_RESTORE_OUTPUTS_SUMMARY'] = (
        'Return the resolved output-restore behavior for this run.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_WILL_RESTORE_OUTPUTS_DETAILS'] = dedent("""\
        Returns:
            RestoreOutputsOptions.Literals: Effective restore behavior after applying
                config-following rules.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_TO_USE_SUMMARY'] = (
        'Return the resolved storage protocol used for persisted outputs.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_TO_USE_DETAILS'] = (
        dedent("""\
        Returns:
            OutputStorageProtocolOptions.Literals: Effective storage protocol for this
                run.
    """))

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_RESULT_KEY_SUMMARY'] = (
        'Return the dictionary key used to wrap results, if configured.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_RESULT_KEY_DETAILS'] = dedent("""\
        Returns:
            str | None: Result wrapper key, or ``None`` when results are returned raw.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_FIXED_PARAMS_SUMMARY'] = (
        'Return parameters that are always supplied when the job callable runs.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_FIXED_PARAMS_DETAILS'] = dedent("""\
        Returns:
            MappingProxyType[str, object]: Read-only mapping of fixed keyword values.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_PARAM_KEY_MAP_SUMMARY'] = (
        'Return keyword-name remappings applied before calling the job callable.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_PARAM_KEY_MAP_DETAILS'] = dedent("""\
        Returns:
            MappingProxyType[str, str]: Mapping from external keyword names to callable
                parameter names.
    """)

    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_GET_BOUND_ARGS_SUMMARY'] = (
        'Bind arguments to the job callable signature.')
    os.environ['OMNIPY_MACRO_ISFUNCARGJOBBASE_GET_BOUND_ARGS_DETAILS'] = dedent("""\
        Args:
            *args: Positional call arguments.
            **kwargs: Keyword call arguments.

        Returns:
            inspect.BoundArguments: Bound arguments with defaults applied.
    """)

    os.environ['OMNIPY_MACRO_ISJOB_TIME_OF_CUR_TOPLEVEL_FLOW_RUN_SUMMARY'] = (
        'Return the start time of the active top-level flow run, if any.')
    os.environ['OMNIPY_MACRO_ISJOB_TIME_OF_CUR_TOPLEVEL_FLOW_RUN_DETAILS'] = dedent("""\
        Returns:
            datetime | None: Timestamp for the current outermost flow run, or ``None``.
    """)

    os.environ['OMNIPY_MACRO_ISJOB_CREATE_JOB_SUMMARY'] = (
        'Create an applied job instance from the concrete job class.')
    os.environ['OMNIPY_MACRO_ISJOB_CREATE_JOB_DETAILS'] = dedent("""\
        Args:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            _JobT: New applied job instance.
    """)

    os.environ['OMNIPY_MACRO_ISJOB_REVISE_SUMMARY'] = (
        'Return a template reconstructed from this applied job.')
    os.environ['OMNIPY_MACRO_ISJOB_REVISE_DETAILS'] = dedent("""\
        Returns:
            _JobTemplateT: Template carrying the current job configuration.
    """)

    os.environ['OMNIPY_MACRO_ISJOBTEMPLATE_CREATE_JOB_TEMPLATE_SUMMARY'] = (
        'Create a job template instance from the concrete template class.')
    os.environ['OMNIPY_MACRO_ISJOBTEMPLATE_CREATE_JOB_TEMPLATE_DETAILS'] = dedent("""\
        Args:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            _JobTemplateT: New job template instance.
    """)

    os.environ['OMNIPY_MACRO_ISJOBTEMPLATE_RUN_SUMMARY'] = (
        'Apply the template and execute the resulting job immediately.')
    os.environ['OMNIPY_MACRO_ISJOBTEMPLATE_RUN_DETAILS'] = dedent("""\
        Args:
            *args: Positional arguments passed to the applied job.
            **kwargs: Keyword arguments passed to the applied job.

        Returns:
            _RetCovT: Result returned by the applied job.
    """)

    os.environ['OMNIPY_MACRO_ISJOBTEMPLATE_APPLY_SUMMARY'] = (
        'Create an applied job from this template without executing it.')
    os.environ['OMNIPY_MACRO_ISJOBTEMPLATE_APPLY_DETAILS'] = dedent("""\
        Returns:
            _JobT: Applied job instance ready to be called.
    """)


class HasJobCreator(Protocol):
    """Protocol for objects exposing a shared :class:`IsJobCreator` instance."""
    @property
    def job_creator(self) -> IsJobCreator:
        """Return the shared creator object backing the job family.

        Returns:
            IsJobCreator: Shared holder for engine, config, and nested-context state.
        """
        ...


class IsJobBase(CanLog, IsUniquelyNamedJob, Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Common protocol shared by job templates and applied jobs.

    Implementations expose stable naming, logging, configuration, and the
    lifecycle hooks used to move between template, applied-job, and run states.
    """
    @property
    def _job_creator(self) -> IsJobCreator:
        ...

    @property
    def config(self) -> IsJobConfig:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBBASE_CONFIG_SUMMARY}}
        #
        # {{ISJOBBASE_CONFIG_DETAILS}}
        """Return the job configuration visible to this instance.

        Returns:
            IsJobConfig: Active job configuration used for runtime behavior.
        """
        ...

    @property
    def engine(self) -> IsEngine | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBBASE_ENGINE_SUMMARY}}
        #
        # {{ISJOBBASE_ENGINE_DETAILS}}
        """Return the engine associated with this job, if any.

        Returns:
            IsEngine | None: Engine used for decoration and execution, or ``None``.
        """
        ...

    @property
    def in_flow_context(self) -> bool:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBBASE_IN_FLOW_CONTEXT_SUMMARY}}
        #
        # {{ISJOBBASE_IN_FLOW_CONTEXT_DETAILS}}
        """Return whether the job is currently executing inside a flow context.

        Returns:
            bool: ``True`` when a surrounding flow context is active.
        """
        ...

    def __eq__(self, other: object) -> bool:
        ...

    @classmethod
    def _create_job_template(cls, *args: object, **kwargs: object) -> _JobTemplateT:
        ...

    @classmethod
    def _create_job(cls, *args: object, **kwargs: object) -> _JobT:
        ...

    def _apply(self) -> _JobT:
        ...

    def _refine(self, *args: Any, update: bool = True, **kwargs: object) -> _JobTemplateT:
        ...

    def _revise(self) -> _JobTemplateT:
        ...

    def _call_job_template(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...

    def _call_job(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...


class IsFuncArgJobBase(Protocol):
    """Protocol for jobs backed by a Python callable and callable-related options.

    This contract adds signature inspection, dataset-iteration controls, result
    shaping, and persisted-output settings on top of the base job lifecycle.
    """
    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
        """Return the inspected parameter signature of the job callable.

        Returns:
            MappingProxyType[str, inspect.Parameter]: Mapping from parameter names to
                signature entries.
        """
        ...

    @property
    def return_type(self) -> type:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_RETURN_TYPE_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_RETURN_TYPE_DETAILS}}
        """Return the annotated return type of the job callable.

        Returns:
            type: Return annotation for the callable.
        """
        ...

    @property
    def iterate_over_data_files(self) -> bool:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_ITERATE_OVER_DATA_FILES_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_ITERATE_OVER_DATA_FILES_DETAILS}}
        """Return whether the job should iterate over dataset items automatically.

        Returns:
            bool: ``True`` when the first dataset argument is expanded item-by-item.
        """
        ...

    @property
    def output_dataset_param(self) -> str | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_OUTPUT_DATASET_PARAM_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_OUTPUT_DATASET_PARAM_DETAILS}}
        """Return the parameter name used for an explicit output dataset, if any.

        Returns:
            str | None: Output-dataset parameter name, or ``None`` when not configured.
        """
        ...

    @property
    def output_dataset_cls(self) -> type[IsDataset] | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_OUTPUT_DATASET_CLS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_OUTPUT_DATASET_CLS_DETAILS}}
        """Return the dataset class used for iterated outputs, if configured.

        Returns:
            type[IsDataset] | None: Output dataset type, or ``None`` when inferred.
        """
        ...

    @property
    def auto_async(self) -> bool:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_AUTO_ASYNC_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_AUTO_ASYNC_DETAILS}}
        """Return whether coroutine jobs should auto-run outside flow contexts.

        Returns:
            bool: ``True`` when coroutine jobs are automatically awaited or scheduled.
        """
        ...

    @property
    def persist_outputs(self) -> PersistOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_PERSIST_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_PERSIST_OUTPUTS_DETAILS}}
        """Return the configured per-job output-persistence preference.

        Returns:
            PersistOutputsOptions.Literals: Persistence setting before config fallback.
        """
        ...

    @property
    def restore_outputs(self) -> RestoreOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_RESTORE_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_RESTORE_OUTPUTS_DETAILS}}
        """Return the configured per-job output-restore preference.

        Returns:
            RestoreOutputsOptions.Literals: Restore setting before config fallback.
        """
        ...

    @property
    def output_storage_protocol(self) -> OutputStorageProtocolOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_DETAILS}}
        """Return the configured output-storage protocol preference.

        Returns:
            OutputStorageProtocolOptions.Literals: Storage-protocol setting before
                config fallback.
        """
        ...

    @property
    def will_persist_outputs(self) -> PersistOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_WILL_PERSIST_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_WILL_PERSIST_OUTPUTS_DETAILS}}
        """Return the resolved output-persistence behavior for this run.

        Returns:
            PersistOutputsOptions.Literals: Effective persistence behavior after
                applying config-following rules.
        """
        ...

    @property
    def will_restore_outputs(self) -> RestoreOutputsOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_WILL_RESTORE_OUTPUTS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_WILL_RESTORE_OUTPUTS_DETAILS}}
        """Return the resolved output-restore behavior for this run.

        Returns:
            RestoreOutputsOptions.Literals: Effective restore behavior after applying
                config-following rules.
        """
        ...

    @property
    def output_storage_protocol_to_use(self) -> OutputStorageProtocolOptions.Literals:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_TO_USE_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_OUTPUT_STORAGE_PROTOCOL_TO_USE_DETAILS}}
        """Return the resolved storage protocol used for persisted outputs.

        Returns:
            OutputStorageProtocolOptions.Literals: Effective storage protocol for this
                run.
        """
        ...

    @property
    def result_key(self) -> str | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_RESULT_KEY_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_RESULT_KEY_DETAILS}}
        """Return the dictionary key used to wrap results, if configured.

        Returns:
            str | None: Result wrapper key, or ``None`` when results are returned raw.
        """
        ...

    @property
    def fixed_params(self) -> MappingProxyType[str, object]:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_FIXED_PARAMS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_FIXED_PARAMS_DETAILS}}
        """Return parameters that are always supplied when the job callable runs.

        Returns:
            MappingProxyType[str, object]: Read-only mapping of fixed keyword values.
        """
        ...

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_PARAM_KEY_MAP_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_PARAM_KEY_MAP_DETAILS}}
        """Return keyword-name remappings applied before calling the job callable.

        Returns:
            MappingProxyType[str, str]: Mapping from external keyword names to callable
                parameter names.
        """
        ...

    @property
    def callable_type(self) -> CallableType.Literals:
        """
        The effective callable type of the job function.

        The callable type captures both the synchronous/asynchronous and
        plain/generator dimensions of the wrapped callable.

        Returns:
            CallableType.Literals: The effective callable type of the job
                function.
        """
        ...

    def get_bound_args(self, *args: object, **kwargs: object) -> inspect.BoundArguments:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_GET_BOUND_ARGS_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_GET_BOUND_ARGS_DETAILS}}
        """Bind arguments to the job callable signature.

        Args:
            *args: Positional call arguments.
            **kwargs: Keyword call arguments.

        Returns:
            inspect.BoundArguments: Bound arguments with defaults applied.
        """
        ...


class IsPlainFuncArgJobBase(Protocol):
    """Minimal protocol for objects that store and decorate a wrapped callable."""

    _job_func: Callable

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        ...


_CallableT = TypeVar('_CallableT', bound=Callable)


class IsJobBaseCallable(IsJobBase[_JobTemplateT, _JobT, _CallP, _RetCovT],
                        Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Protocol for job objects that expose a normal callable interface.

    Templates and applied jobs both satisfy this contract, but they may route
    calls differently depending on whether they are inside a flow context.
    """
    def __call__(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        ...


@runtime_checkable
class IsJob(IsJobBaseCallable[_JobTemplateT, _JobT, _CallP, _RetCovT],
            Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Protocol for an applied job that is ready to execute.

    Applied jobs carry runtime state such as engine decoration and flow-run
    timing, and they can be revised back into templates when needed.
    """
    @property
    def time_of_cur_toplevel_flow_run(self) -> datetime | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOB_TIME_OF_CUR_TOPLEVEL_FLOW_RUN_SUMMARY}}
        #
        # {{ISJOB_TIME_OF_CUR_TOPLEVEL_FLOW_RUN_DETAILS}}
        """Return the start time of the active top-level flow run, if any.

        Returns:
            datetime | None: Timestamp for the current outermost flow run, or ``None``.
        """
        ...

    @classmethod
    def create_job(cls, *args: object, **kwargs: object) -> _JobT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOB_CREATE_JOB_SUMMARY}}
        #
        # {{ISJOB_CREATE_JOB_DETAILS}}
        """Create an applied job instance from the concrete job class.

        Args:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            _JobT: New applied job instance.
        """
        ...

    def revise(self) -> _JobTemplateT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOB_REVISE_SUMMARY}}
        #
        # {{ISJOB_REVISE_DETAILS}}
        """Return a template reconstructed from this applied job.

        Returns:
            _JobTemplateT: Template carrying the current job configuration.
        """
        ...

    def _apply_engine_decorator(self, engine: IsEngine) -> None:
        ...


@runtime_checkable
class IsJobTemplate(IsJobBaseCallable[_JobTemplateT, _JobT, _CallP, _RetCovT],
                    Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Protocol for a reusable job template with immutable configuration.

    Templates can be created, refined, applied to produce runnable jobs, or run
    directly through the apply-and-execute convenience path.
    """
    @classmethod
    def create_job_template(cls, *args: object, **kwargs: object) -> _JobTemplateT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBTEMPLATE_CREATE_JOB_TEMPLATE_SUMMARY}}
        #
        # {{ISJOBTEMPLATE_CREATE_JOB_TEMPLATE_DETAILS}}
        """Create a job template instance from the concrete template class.

        Args:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            _JobTemplateT: New job template instance.
        """
        ...

    def run(self, *args: _CallP.args, **kwargs: _CallP.kwargs) -> _RetCovT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBTEMPLATE_RUN_SUMMARY}}
        #
        # {{ISJOBTEMPLATE_RUN_DETAILS}}
        """Apply the template and execute the resulting job immediately.

        Args:
            *args: Positional arguments passed to the applied job.
            **kwargs: Keyword arguments passed to the applied job.

        Returns:
            _RetCovT: Result returned by the applied job.
        """
        ...

    def apply(self) -> _JobT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBTEMPLATE_APPLY_SUMMARY}}
        #
        # {{ISJOBTEMPLATE_APPLY_DETAILS}}
        """Create an applied job from this template without executing it.

        Returns:
            _JobT: Applied job instance ready to be called.
        """
        ...


class IsFuncArgJobTemplate(IsJobTemplate[_JobTemplateT, _JobT, _CallP, _RetCovT],
                           IsFuncArgJobBase,
                           Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Template protocol for callable-backed tasks and function-style flows.

    Implementations refine the wrapped callable's execution options without
    changing the public callable contract seen by template consumers.
    """
    def refine(
            self,
            *args: Any,
            update: bool = True,
            name: str | None = None,
            iterate_over_data_files: bool = False,
            output_dataset_param: str | None = None,
            output_dataset_cls: type[IsDataset] | None = None,
            auto_async: bool = True,
            result_key: str | None = None,
            fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
            param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
            persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
            restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
            **kwargs: object) -> _JobTemplateT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Return a template with updated callable-configuration settings.
        #
        # Args:
        #     *args: Positional constructor overrides for the template.
        #
        # {{JOB_TEMPLATE_REFINE_COMMON_ARGS}}
        #
        """Return a template with updated callable-configuration settings.

        Args:
            *args: Positional constructor overrides for the template.

            update: Whether omitted values should be inherited from the current template.
            name: Optional replacement display name.
            iterate_over_data_files: Whether dataset inputs should be processed item-wise.
            output_dataset_param: Optional name of an explicit output-dataset parameter.
            output_dataset_cls: Optional dataset class to use for iterated outputs.
            auto_async: Whether coroutine jobs should auto-run outside flow contexts.
            result_key: Optional key used to wrap the returned result in a dictionary.
            fixed_params: Keyword arguments fixed onto every job invocation.
            param_key_map: Mapping from external keyword names to callable parameter names.
            persist_outputs: Per-job output-persistence preference.
            restore_outputs: Per-job output-restore preference.
            **kwargs: Additional constructor keyword overrides.

        Returns:
            _JobTemplateT: Refined template instance.

        """
        ...


class HasFuncArgJobTemplateInit(Protocol[_JobTemplateT, _CallP, _RetContraT]):
    """Callable initializer protocol for templates that wrap one Python callable.

    This is the decorator-facing constructor shape used by task templates and
    callable-backed flow templates.
    """
    def __call__(
        self,
        job_func: Callable[_CallP, _RetContraT],
        *,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        output_dataset_param: str | None = None,
        output_dataset_cls: type[IsDataset] | None = None,
        auto_async: bool = True,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
        restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
        **kwargs: object,
    ) -> _JobTemplateT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Create a job template around ``job_func``.
        #
        # Args:
        # {{JOB_TEMPLATE_INIT_CALL_COMMON_ARGS}}
        """Create a job template around ``job_func``.

        Args:
            job_func: Python callable to wrap as a job template.
            name: Optional replacement display name.
            iterate_over_data_files: Whether dataset inputs should be processed item-wise.
            output_dataset_param: Optional name of an explicit output-dataset parameter.
            output_dataset_cls: Optional dataset class to use for iterated outputs.
            auto_async: Whether coroutine jobs should auto-run outside flow contexts.
            result_key: Optional key used to wrap the returned result in a dictionary.
            fixed_params: Keyword arguments fixed onto every job invocation.
            param_key_map: Mapping from external keyword names to callable parameter names.
            persist_outputs: Per-job output-persistence preference.
            restore_outputs: Per-job output-restore preference.
            **kwargs: Additional constructor keyword overrides.

        Returns:
            _JobTemplateT: New job template instance wrapping ``job_func``.
        """
        ...


class IsChildJobListArgJobBase(IsFuncArgJobBase, Protocol):
    """Protocol for flow-style jobs that own an ordered child-template list.

    The child templates define the nested jobs a flow applies or orchestrates in
    addition to its own callable-backed configuration.
    """
    @property
    def child_job_templates(self) -> tuple[IsFuncArgJobTemplate, ...]:
        """Return the child-job templates owned by the flow template.

        Returns:
            tuple[IsFuncArgJobTemplate, ...]: Ordered child-job templates.
        """
        ...


class HasChildJobListArgJobTemplateInit(Protocol[_JobTemplateT, _CallP, _RetContraT]):
    """Callable initializer protocol for flow templates with child job templates.

    The initializer receives both the coordinating callable and the ordered child
    templates that make up the flow body.
    """
    def __call__(
        self,
        job_func: Callable[_CallP, _RetContraT],
        /,
        *child_job_templates: IsFuncArgJobTemplate,
        name: str | None = None,
        iterate_over_data_files: bool = False,
        output_dataset_param: str | None = None,
        output_dataset_cls: type[IsDataset] | None = None,
        auto_async: bool = True,
        result_key: str | None = None,
        fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
        param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
        persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
        restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
        **kwargs: object,
    ) -> _JobTemplateT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Create a flow template around ``job_func`` and child jobs.
        #
        # Args:
        #     *child_job_templates: Ordered child-job templates owned by the flow template.
        #
        # {{JOB_TEMPLATE_INIT_CALL_COMMON_ARGS}}
        """Create a flow template around ``job_func`` and child jobs.

        Args:
            *child_job_templates: Ordered child-job templates owned by the flow template.

            job_func: Python callable to wrap as a job template.
            name: Optional replacement display name.
            iterate_over_data_files: Whether dataset inputs should be processed item-wise.
            output_dataset_param: Optional name of an explicit output-dataset parameter.
            output_dataset_cls: Optional dataset class to use for iterated outputs.
            auto_async: Whether coroutine jobs should auto-run outside flow contexts.
            result_key: Optional key used to wrap the returned result in a dictionary.
            fixed_params: Keyword arguments fixed onto every job invocation.
            param_key_map: Mapping from external keyword names to callable parameter names.
            persist_outputs: Per-job output-persistence preference.
            restore_outputs: Per-job output-restore preference.
            **kwargs: Additional constructor keyword overrides.

        Returns:
            _JobTemplateT: New job template instance wrapping ``job_func``.
        """
        ...


if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISFLOW_FLOW_CONTEXT_SUMMARY'] = (
        'Return a context manager that enters and exits the shared flow context.')
    os.environ['OMNIPY_MACRO_ISFLOW_FLOW_CONTEXT_DETAILS'] = dedent("""\
        Returns:
            IsNestedContext: Context manager that tracks top-level flow execution state.
    """)

    os.environ['OMNIPY_MACRO_ISFLOW_TIME_OF_LAST_RUN_SUMMARY'] = (
        'Return the timestamp captured for the most recent top-level flow run.')
    os.environ['OMNIPY_MACRO_ISFLOW_TIME_OF_LAST_RUN_DETAILS'] = dedent("""\
        Returns:
            datetime | None: Timestamp from the latest top-level flow run, or ``None`` if the
                flow has not completed one yet.
    """)


class IsTaskTemplate(IsFuncArgJobTemplate['IsTaskTemplate[_CallP, _RetT]',
                                          'IsTask[_CallP, _RetT]',
                                          _CallP,
                                          _RetT],
                     Protocol[_CallP, _RetT]):
    """
    Loosely coupled type replacement for the :py:class:`~omnipy.compute.task.TaskTemplate` class
    """
    ...


class IsFuncArgJob(IsJob[_JobTemplateT, _JobT, _CallP, _RetCovT],
                   IsFuncArgJobBase,
                   Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Applied-job protocol for callable-backed tasks and flows."""


class IsTask(IsFuncArgJob['IsTaskTemplate[_CallP, _RetT]', 'IsTask[_CallP, _RetT]', _CallP, _RetT],
             Protocol[_CallP, _RetT]):
    """Protocol for an applied Omnipy task.

    A task represents one runnable callable-backed compute step with no owned
    child job templates.
    """

    ...


class IsFlowTemplate(Protocol):
    """Protocol for flow templates."""

    ...


class IsFlow(Protocol):
    """Protocol for applied flows with run-state metadata."""
    @property
    def flow_context(self) -> IsNestedContext:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFLOW_FLOW_CONTEXT_SUMMARY}}
        #
        # {{ISFLOW_FLOW_CONTEXT_DETAILS}}
        """Return a context manager that enters and exits the shared flow context.

        Returns:
            IsNestedContext: Context manager that tracks top-level flow execution state.
        """
        ...

    @property
    def time_of_last_run(self) -> datetime | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFLOW_TIME_OF_LAST_RUN_SUMMARY}}
        #
        # {{ISFLOW_TIME_OF_LAST_RUN_DETAILS}}
        """Return the timestamp captured for the most recent top-level flow run.

        Returns:
            datetime | None: Timestamp from the latest top-level flow run, or ``None`` if the
                flow has not completed one yet.
        """
        ...


class IsChildJobListArgJobTemplate(IsFuncArgJobTemplate[_JobTemplateT, _JobT, _CallP, _RetCovT],
                                   IsChildJobListArgJobBase,
                                   Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """Template protocol for flows composed from an ordered child-template list.

    Refinement can replace the owned child templates while keeping the shared
    callable-backed configuration contract from :class:`IsFuncArgJobTemplate`.
    """
    def refine(
            self,
            *child_job_templates: IsFuncArgJobTemplate,
            update: bool = True,
            name: str | None = None,
            iterate_over_data_files: bool = False,
            output_dataset_param: str | None = None,
            output_dataset_cls: type[IsDataset] | None = None,
            auto_async: bool = True,
            result_key: str | None = None,
            fixed_params: Mapping[str, object] | Iterable[tuple[str, object]] | None = None,
            param_key_map: Mapping[str, str] | Iterable[tuple[str, str]] | None = None,
            persist_outputs: PersistOutputsOptions.Literals = PersistOutputsOptions.FOLLOW_CONFIG,
            restore_outputs: RestoreOutputsOptions.Literals = RestoreOutputsOptions.FOLLOW_CONFIG,
            **kwargs: object) -> _JobTemplateT:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # Return a flow template with updated child jobs or callable configuration.
        #
        # Args:
        #     *child_job_templates: Replacement ordered child-job templates.
        #
        # {{JOB_TEMPLATE_REFINE_COMMON_ARGS}}
        #
        """Return a flow template with updated child jobs or callable configuration.

        Args:
            *child_job_templates: Replacement ordered child-job templates.

            update: Whether omitted values should be inherited from the current template.
            name: Optional replacement display name.
            iterate_over_data_files: Whether dataset inputs should be processed item-wise.
            output_dataset_param: Optional name of an explicit output-dataset parameter.
            output_dataset_cls: Optional dataset class to use for iterated outputs.
            auto_async: Whether coroutine jobs should auto-run outside flow contexts.
            result_key: Optional key used to wrap the returned result in a dictionary.
            fixed_params: Keyword arguments fixed onto every job invocation.
            param_key_map: Mapping from external keyword names to callable parameter names.
            persist_outputs: Per-job output-persistence preference.
            restore_outputs: Per-job output-restore preference.
            **kwargs: Additional constructor keyword overrides.

        Returns:
            _JobTemplateT: Refined template instance.

        """
        ...


class IsLinearFlowTemplate(IsChildJobListArgJobTemplate['IsLinearFlowTemplate[_CallP, _RetCovT]',
                                                        'IsLinearFlow[_CallP, _RetCovT]',
                                                        _CallP,
                                                        _RetCovT],
                           IsFlowTemplate,
                           Protocol[_CallP, _RetCovT]):
    """Protocol for linear flow templates."""

    ...


class IsChildJobListArgJob(IsChildJobListArgJobBase,
                           IsFuncArgJob[_JobTemplateT, _JobT, _CallP, _RetCovT],
                           Protocol[_JobTemplateT, _JobT, _CallP, _RetCovT]):
    """"""


class IsLinearFlow(IsChildJobListArgJob['IsLinearFlowTemplate[_CallP, _RetCovT]',
                                        'IsLinearFlow[_CallP, _RetCovT]',
                                        _CallP,
                                        _RetCovT],
                   IsFlow,
                   Protocol[_CallP, _RetCovT]):
    """Protocol for applied linear flows."""

    ...


class IsDagFlowTemplate(IsChildJobListArgJobTemplate['IsDagFlowTemplate[_CallP, _RetCovT]',
                                                     'IsDagFlow[_CallP, _RetCovT]',
                                                     _CallP,
                                                     _RetCovT],
                        IsFlowTemplate,
                        Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsDagFlow(IsChildJobListArgJob['IsDagFlowTemplate[_CallP, _RetCovT]',
                                     'IsDagFlow[_CallP, _RetCovT]',
                                     _CallP,
                                     _RetCovT],
                IsFlow,
                Protocol[_CallP, _RetCovT]):
    """Protocol for applied DAG flows."""

    ...


class IsFuncFlowTemplate(IsFuncArgJobTemplate['IsFuncFlowTemplate[_CallP, _RetCovT]',
                                              'IsFuncFlow[_CallP, _RetCovT]',
                                              _CallP,
                                              _RetCovT],
                         IsFlowTemplate,
                         Protocol[_CallP, _RetCovT]):
    """Protocol for callable-backed flow templates."""

    ...


class IsFuncFlow(IsFuncArgJob['IsFuncFlowTemplate[_CallP, _RetCovT]',
                              'IsFuncFlow[_CallP, _RetCovT]',
                              _CallP,
                              _RetCovT],
                 IsFlow,
                 Protocol[_CallP, _RetCovT]):
    """Protocol for callable-backed applied flows."""

    ...


class IsAnyFlowTemplate(IsFuncArgJobTemplate['IsAnyFlowTemplate[_CallP, _RetCovT]',
                                             'IsAnyFlow[_CallP, _RetCovT]',
                                             _CallP,
                                             _RetCovT],
                        IsFlowTemplate,
                        Protocol[_CallP, _RetCovT]):
    """"""
    ...


class IsAnyFlow(IsFuncArgJob['IsAnyFlowTemplate[_CallP, _RetCovT]',
                             'IsAnyFlow[_CallP, _RetCovT]',
                             _CallP,
                             _RetCovT],
                IsFlow,
                Protocol[_CallP, _RetCovT]):
    """Protocol covering any applied Omnipy flow variant.

    This union-style flow contract is useful where task, linear-flow, DAG-flow,
    and function-flow implementations are all accepted.
    """
    ...
