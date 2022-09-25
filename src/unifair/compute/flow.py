from typing import Any, Optional, Tuple, Type, Union

from unifair.compute.job import Job, JobConfig, JobTemplate


class FlowConfig(JobConfig):
    def __init__(self, *, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name=name, **kwargs)

        if self._name is not None:
            self._check_not_empty_string('name', self.name)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class FlowTemplate(JobTemplate, FlowConfig):
    def __init__(self, *args: Any, **kwargs: Any):  # noqa
        if self.__class__ is FlowTemplate:
            raise RuntimeError('FlowTemplate can only be instantiated '
                               'through one of its subclasses')
        super().__init__(*args, **kwargs)

    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return Flow


class Flow(Job, FlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return FlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return FlowTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass


class DagFlowConfig(FlowConfig):
    def __init__(self, *, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class DagFlowTemplate(FlowTemplate, DagFlowConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return DagFlow


class DagFlow(Flow, DagFlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return DagFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return DagFlowTemplate


class FuncFlowConfig(FlowConfig):
    def __init__(self, *, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name=name, **kwargs)

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class FuncFlowTemplate(FlowTemplate, FuncFlowConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return FuncFlow


class FuncFlow(Flow, FuncFlowConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return FuncFlowConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return FuncFlowTemplate
