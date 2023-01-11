import inspect
from types import MappingProxyType
from typing import Iterable, Type


class SignatureFuncJobBaseMixin:
    def __init__(self):
        self._func_signature = inspect.signature(self._job_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._func_signature.parameters

    @property
    def return_type(self) -> Type[object]:
        return self._func_signature.return_annotation

    def _check_param_keys_in_func_signature(self,
                                            param_keys: Iterable[str],
                                            modifier_kwarg_key: str) -> None:
        for param_key in param_keys:
            if param_key not in self.param_signatures:
                raise KeyError('Parameter "{}" was not found in the '.format(param_key)
                               + 'signature of the job function. Only parameters in the '
                               'signature of the job function are '
                               f'allowed as keys in the "{modifier_kwarg_key}" modifier.')
