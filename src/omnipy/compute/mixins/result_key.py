from typing import cast

from omnipy.api.protocols.private.compute.job import IsJobBase
from omnipy.compute.mixins.name import NameJobBaseMixin


class ResultKeyFuncJobBaseMixin:
    def __init__(self, *, result_key: str | None = None):
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)

        self._result_key = result_key

        if self.result_key is not None:
            self_as_name_job_base_mixin._check_not_empty_string('result_key', self.result_key)

    @property
    def result_key(self) -> str | None:
        return self._result_key

    def _call_job(self, *args: object, **kwargs: object) -> object:
        super_as_job_base = cast(IsJobBase, super())
        result = super_as_job_base._call_job(*args, **kwargs)

        if self._result_key:
            return {self._result_key: result}
        else:
            return result
