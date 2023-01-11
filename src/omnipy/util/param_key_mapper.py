from typing import Any, Dict


class ParamKeyMapper:
    def __init__(self, key_map: Dict[str, str]):
        self.key_map = dict(key_map)
        self._inverse_key_map = {val: key for key, val in self.key_map.items()}

        if len(self.key_map) != len(self._inverse_key_map):
            raise ValueError('Some values were dropped when translating to the inverse key_map!')

    def _get_key_map(self, inverse: bool):
        return self._inverse_key_map if inverse else self.key_map

    def map_matching_keys(self, params: Dict[str, Any], inverse: bool,
                          keep_non_matching_keys: bool):
        key_map = self._get_key_map(inverse)
        keys = params.keys() if keep_non_matching_keys else [
            key for key in params if key in key_map
        ]
        return {key_map[key] if key in key_map else key: params[key] for key in keys}

    def delete_matching_keys(self, params: Dict[str, Any], inverse: bool):
        key_map = self._get_key_map(inverse)
        return {key: params[key] for key in params if key not in key_map}

    def map_matching_keys_delete_inverse_matches_keep_rest(self,
                                                           params: Dict[str, Any],
                                                           inverse: bool):
        params = self.delete_matching_keys(params, not inverse)
        params = self.map_matching_keys(params, inverse, keep_non_matching_keys=True)

        return params
