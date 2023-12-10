from types import MappingProxyType
from typing import cast, Mapping

from omnipy.api.protocols.private.compute.job import IsJobBase
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.name import NameJobBaseMixin
from omnipy.util.helpers import repr_max_len
from omnipy.util.param_key_mapper import ParamKeyMapper


class ParamsFuncJobBaseMixin:
    def __init__(
        self,
        *,
        fixed_params: Mapping[str, object] | None = None,
        param_key_map: Mapping[str, str] | None = None,
    ):
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)

        self._fixed_params = dict(fixed_params) if fixed_params is not None else {}
        self._param_key_mapper = ParamKeyMapper(param_key_map if param_key_map is not None else {})

        self_as_signature_func_job_base_mixin._check_param_keys_in_func_signature(
            self.fixed_params.keys(), 'fixed_params')
        self_as_signature_func_job_base_mixin._check_param_keys_in_func_signature(
            self.param_key_map.keys(), 'param_key_map')

    @property
    def fixed_params(self) -> MappingProxyType[str, object]:
        return MappingProxyType(self._fixed_params)

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        return MappingProxyType(self._param_key_mapper.key_map)

    def _call_job(self, *args: object, **kwargs: object) -> object:
        self_as_name_job_base_mixin = cast(NameJobBaseMixin, self)
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)

        mapped_fixed_params = self._param_key_mapper.delete_matching_keys(
            self._fixed_params, inverse=True)
        mapped_kwargs = self._param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
            kwargs, inverse=True)
        try:
            if len(mapped_kwargs) < len(kwargs):
                raise TypeError('Keyword arguments {} matches parameter key map inversely.'.format(
                    tuple(set(kwargs.keys()) - set(mapped_kwargs.keys()))))

            super_as_job_base = cast(IsJobBase, super())
            result = super_as_job_base._call_job(*args, **mapped_fixed_params, **mapped_kwargs)

        except TypeError as e:
            if str(e).startswith('Incorrect job function arguments'):
                signature_values = self_as_signature_func_job_base_mixin.param_signatures.values()
                raise TypeError(f'Incorrect job function arguments for job '
                                f'"{self_as_name_job_base_mixin.name}"!\n'
                                f'Job class name: {self.__class__.__name__}\n'
                                f'Current parameter key map contents: {self.param_key_map}\n'
                                f'Positional arguments: {repr_max_len(args)}\n'
                                f'Keyword arguments: {repr_max_len(kwargs)}\n'
                                f'Mapped fixed parameters: {repr_max_len(mapped_fixed_params)}\n'
                                f'Mapped keyword arguments: {repr_max_len(mapped_kwargs)}\n'
                                f'Call function signature parameters: '
                                f'{[(str(p), p.kind) for p in signature_values]}') from e
            else:
                raise

        return result
