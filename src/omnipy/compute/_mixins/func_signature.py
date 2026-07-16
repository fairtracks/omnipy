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
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFUNCARGJOBBASE_RETURN_TYPE_SUMMARY}}
        #
        # {{ISFUNCARGJOBBASE_RETURN_TYPE_DETAILS}}
        """Return the annotated return type of the job callable.

        Returns:
            type: Return annotation for the callable.
        """

        return self._func_signature.return_annotation

    def _check_param_keys_do_not_target_var_params(self,
                                                   param_keys: Iterable[str],
                                                   modifier_kwarg_key: str) -> None:
        """Reject direct targeting of ``*args``/``**kwargs`` parameter names.

        Parameter-modifier APIs such as ``fixed_params`` and
        ``param_key_map`` operate on concrete callable parameter names.
        Var-positional and var-keyword parameters collect arguments
        structurally rather than through a meaningful caller-facing key,
        so their parameter names may not be targeted directly.
        """
        var_param_kinds_by_name = {
            param.name: param.kind
            for param in self.param_signatures.values()
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        }

        if not var_param_kinds_by_name:
            return

        for param_key in param_keys:
            if param_key in var_param_kinds_by_name:
                param_kind = var_param_kinds_by_name[param_key]
                raise KeyError(
                    f'Parameter "{param_key}" is a {param_kind.name} parameter in the job '
                    'function signature, so it may not be targeted directly by the '
                    f'"{modifier_kwarg_key}" modifier. Target concrete keyword names '
                    'instead.')

    def _check_param_keys_in_func_signature(self,
                                            param_keys: Iterable[str],
                                            modifier_kwarg_key: str) -> None:
        """Validate modifier keys against the job function signature.

        In addition to checking that targeted names exist, this rejects
        direct targeting of var-positional and var-keyword parameter
        names.
        """
        self._check_param_keys_do_not_target_var_params(param_keys, modifier_kwarg_key)

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

        bound_args = self._func_signature.bind(*args, **kwargs)
        bound_args.apply_defaults()
        return bound_args
