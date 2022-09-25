from typing import Any, Tuple, Type, Union

from unifair.compute.job import Job, JobConfig, JobTemplate


class FlowConfig(JobConfig):
    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return ()

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return ()


class FlowTemplate(JobTemplate, FlowConfig):
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


class DagFlowTemplate(FlowTemplate):
    pass


class FuncFlowTemplate(FlowTemplate):
    pass


class DagFlow(Flow):
    pass


class FuncFlow(Flow):
    pass
