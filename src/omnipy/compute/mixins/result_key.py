from typing import Optional


class ResultKeyFuncJobBaseMixin:
    # Requires NameJobBaseMixin

    def __init__(self, *, result_key: Optional[str] = None):
        self._result_key = result_key

        if self.result_key is not None:
            self._check_not_empty_string('result_key', self.result_key)

    @property
    def result_key(self) -> Optional[str]:
        return self._result_key

    def _call_job(self, *args: object, **kwargs: object) -> object:

        result = super()._call_job(*args, **kwargs)

        if self._result_key:
            return {self._result_key: result}
        else:
            return result
