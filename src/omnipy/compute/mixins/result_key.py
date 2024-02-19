from typing import cast

from pydantic.fields import Undefined, UndefinedType

from omnipy.api.protocols.private.compute.job import IsJobBase
from omnipy.api.protocols.public.compute import IsTaskTemplate
from omnipy.compute.mixins.name import NameJobBaseMixin


class ResultKeyFuncJobBaseMixin:
    def __init__(self,
                 *,
                 result_key: str | None | UndefinedType = Undefined,
                 default_result_key_for_dag_jobs: str | None | UndefinedType = Undefined,
                 dag_flow_result_selector_key: str | None = None):
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)

        self._result_key = result_key
        self._default_result_key_for_dag_jobs = default_result_key_for_dag_jobs
        self._dag_flow_result_selector_key = dag_flow_result_selector_key

        if self.has_result_key:
            self_as_name_job_base_mixin._check_not_empty_string('result_key', self.result_key)

    @property
    def result_key(self) -> str | UndefinedType | None:
        return self._result_key

    @property
    def has_result_key(self) -> bool:
        return self.result_key is not None and self.result_key is not Undefined

    @property
    def default_result_key_for_dag_jobs(self) -> str | UndefinedType | None:
        return self._default_result_key_for_dag_jobs

    @property
    def dag_flow_result_selector_key(self) -> str | None:
        return self._dag_flow_result_selector_key

    def _call_job(self, *args: object, **kwargs: object) -> object:
        from omnipy.compute.flow import DagFlow

        orig_task_templates: tuple[IsTaskTemplate, ...] = ()

        if isinstance(self, DagFlow):
            if self.default_result_key_for_dag_jobs is not Undefined:
                orig_task_templates = self.task_templates
                self._task_templates = tuple([
                    self._refine_dag_flow_task_template_if_needed(task_template)
                    for task_template in self.task_templates
                ])

        super_as_job_base = cast(IsJobBase, super())
        result = super_as_job_base._call_job(*args, **kwargs)

        # if not isinstance(result, Mapping)

        if isinstance(self, DagFlow):
            self._task_templates = orig_task_templates

            if self.dag_flow_result_selector_key is not None:
                if len(self.task_templates) == 0:
                    assert result == {}
                    return None
                else:
                    try:
                        result = result[self.dag_flow_result_selector_key]
                    except KeyError as e:
                        raise ValueError(
                            'The value for "dag_flow_result_selector_key" does '
                            'not match any keys in the result dictionary of the last task of '
                            f'the DagFlow "{self.unique_name}" '
                            f'("{self.dag_flow_result_selector_key}" not in '
                            f'{result}).') from e
                    except TypeError as e:
                        raise ValueError(
                            'A value is set for "dag_flow_result_selector_key" '
                            f'(="{self.dag_flow_result_selector_key}"), but '
                            f'the result of the last task of the DagFlow "{self.unique_name}" '
                            f'is not a mapping (result={result}).') from e

        if self.has_result_key:
            result = {self._result_key: result}

        return result

    def _refine_dag_flow_task_template_if_needed(self,
                                                 task_template: IsTaskTemplate) -> IsTaskTemplate:
        if task_template.result_key is Undefined:
            return task_template.refine(result_key=self.default_result_key_for_dag_jobs)
        else:
            return task_template
