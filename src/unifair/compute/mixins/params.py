from types import MappingProxyType
from typing import Mapping, Optional

from unifair.util.param_key_mapper import ParamKeyMapper


class ParamsFuncJobConfigMixin:
    # Requires FuncSignatureJobConfigMixin

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


class ParamsFuncJobMixin:
    def __call__(self, *args: object, **kwargs: object) -> object:
        mapped_fixed_params = self._param_key_mapper.delete_matching_keys(
            self._fixed_params, inverse=True)
        mapped_kwargs = self._param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
            kwargs, inverse=True)
        try:
            if len(mapped_kwargs) < len(kwargs):
                raise TypeError('Keyword arguments {} matches parameter key map inversely.'.format(
                    tuple(set(kwargs.keys()) - set(mapped_kwargs.keys()))))

            result = super().__call__(*args, **mapped_fixed_params, **mapped_kwargs)

        except TypeError as e:
            raise TypeError(
                'Incorrect task function arguments. Current parameter key map contents: {}'.format(
                    self.param_key_map)) from e

        return result
