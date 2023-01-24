from types import MappingProxyType
from typing import Mapping, Optional

from omnipy.util.helpers import repr_max_len
from omnipy.util.param_key_mapper import ParamKeyMapper


class ParamsFuncJobBaseMixin:
    # Requires FuncSignatureJobBaseMixin

    def __init__(
        self,
        *,
        fixed_params: Optional[Mapping[str, object]] = None,
        param_key_map: Optional[Mapping[str, str]] = None,
    ):
        self._fixed_params = dict(fixed_params) if fixed_params is not None else {}
        self._param_key_mapper = ParamKeyMapper(param_key_map if param_key_map is not None else {})

        self._check_param_keys_in_func_signature(self.fixed_params.keys(), 'fixed_params')
        self._check_param_keys_in_func_signature(self.param_key_map.keys(), 'param_key_map')

    @property
    def fixed_params(self) -> MappingProxyType[str, object]:
        return MappingProxyType(self._fixed_params)

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        return MappingProxyType(self._param_key_mapper.key_map)

    def _call_job(self, *args: object, **kwargs: object) -> object:

        mapped_fixed_params = self._param_key_mapper.delete_matching_keys(
            self._fixed_params, inverse=True)
        mapped_kwargs = self._param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
            kwargs, inverse=True)
        try:
            if len(mapped_kwargs) < len(kwargs):
                raise TypeError('Keyword arguments {} matches parameter key map inversely.'.format(
                    tuple(set(kwargs.keys()) - set(mapped_kwargs.keys()))))

            result = super()._call_job(*args, **mapped_fixed_params, **mapped_kwargs)

        except TypeError as e:
            if str(e).startswith('Incorrect job function arguments'):
                raise TypeError(
                    f'Incorrect job function arguments for job "{self.name}"!\n'
                    f'Job class name: {self.__class__.__name__}\n'
                    f'Current parameter key map contents: {self.param_key_map}\n'
                    f'Positional arguments: {repr_max_len(args)}\n'
                    f'Keyword arguments: {repr_max_len(kwargs)}\n'
                    f'Mapped fixed parameters: {repr_max_len(mapped_fixed_params)}\n'
                    f'Mapped keyword arguments: {repr_max_len(mapped_kwargs)}\n'
                    f'Call function signature parameters: '
                    f'{[(str(p), p.kind) for p in self.param_signatures.values()]}') from e
            else:
                raise

        return result
