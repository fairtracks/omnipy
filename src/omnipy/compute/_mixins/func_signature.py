"""Mixin for exposing and validating job function signatures."""

from collections.abc import Iterable
import inspect
from types import MappingProxyType
from typing import cast

from omnipy.shared.protocols.compute.job import IsPlainFuncArgJobBase


class SignatureFuncJobBaseMixin:
    """Cache a job function signature and expose signature helpers."""
    def __init__(self):
        self_as_plain_func_arg_job_base = cast(IsPlainFuncArgJobBase, self)
        self._func_signature = inspect.signature(self_as_plain_func_arg_job_base._job_func)
        self.__signature__ = self._func_signature

    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
        return self._func_signature.parameters

    @property
    def return_type(self) -> type:
        """Return the annotated return type of the wrapped job function."""

        return self._func_signature.return_annotation

    def _check_param_keys_in_func_signature(self,
                                            param_keys: Iterable[str],
                                            modifier_kwarg_key: str) -> None:
        if any(param.kind == inspect.Parameter.VAR_KEYWORD
               for param in self.param_signatures.values()):
            return

        for param_key in param_keys:
            if param_key not in self.param_signatures:
                raise KeyError('Parameter "{}" was not found in the '.format(param_key)
                               + 'signature of the job function. Only parameters in the '
                               'signature of the job function are '
                               f'allowed as keys in the "{modifier_kwarg_key}" modifier: '
                               f"{', '.join(key for key in self.param_signatures.keys())}")

    def _update_func_signature(self, new_signature: inspect.Signature):
        # self._job_func.__signature__ = new_signature
        self._func_signature = new_signature
        self.__signature__ = new_signature

    def get_bound_args(self, *args: object, **kwargs: object) -> inspect.BoundArguments:
        """Bind call arguments to the cached job function signature."""

        bound_args = self._func_signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        return bound_args
