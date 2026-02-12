from typing_extensions import TypedDict

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import first_key_in_mapping, first_value_in_mapping


# Currently needed for type checking of the validators, but unfortunately
# violates the DRY principle (Don't Repeat Yourself).
class NameLengthPairDict(TypedDict):
    name: str
    length: int


class SeqColLevel2Dict(TypedDict, extra_items=list[object]):
    lengths: list[int]
    names: list[str]
    sequences: list[str]
    sorted_sequences: list[str]
    name_length_pairs: list[NameLengthPairDict]


def check_equally_long_as_first(value: list[object],
                                values: SeqColLevel2Dict,
                                field: pyd.ModelField) -> list[object]:
    # Currently assumes that all fields are lists
    first_length = len(first_value_in_mapping(values))
    assert len(value) == first_length, \
        (f'Length of fields must be equal, but the length of fields '
         f'{first_key_in_mapping(values)} and {field.name} are not equal: '
         f'{first_length} != {len(value)}')
    return value


class NameLengthPair(pyd.BaseModel):
    name: str
    length: int


class SeqColLevel2Record(pyd.BaseModel):
    lengths: list[int]
    names: list[str]
    sequences: list[str]
    sorted_sequences: list[str] = pyd.Field(default_factory=list)
    name_length_pairs: list[NameLengthPair] = pyd.Field(default_factory=list)

    @pyd.validator('sorted_sequences')
    def set_sorted_sequences(cls, v: list[str], values: SeqColLevel2Dict) -> list[str]:
        if v:
            prev_val = v[0]
            for seq in v[1:]:
                if seq < prev_val:
                    raise ValueError('sorted_sequences must be sorted')
                prev_val = seq
            return v
        else:
            return sorted(values['sequences'])

    @pyd.validator('name_length_pairs')
    def check_name_length_pairs(cls, v: list[NameLengthPair],
                                values: SeqColLevel2Dict) -> list[NameLengthPair]:
        # To avoid key errors if e.g. check_equally_long_as_first fails
        assert all(_ in values for _ in ['names', 'lengths'])

        if v:
            for i, name_length_pair in enumerate(v):
                if i < len(values['names']):
                    assert name_length_pair.name == values['names'][i], \
                        (f'name_length_pairs[{i}].name must match names[{i}], '
                         f'{name_length_pair.name} != {values["names"][i]}')

                if i < len(values['lengths']):
                    assert name_length_pair.length == values['lengths'][i], \
                        (f'name_length_pairs[{i}].length must match lengths[{i}], '
                         f'{name_length_pair.length} != {values["lengths"][i]}')
            return v
        else:
            return [
                NameLengthPair(name=name, length=length)
                for name, length in zip(values['names'], values['lengths'])
            ]

    _names_list_length_equality_validator = pyd.validator(
        'names', allow_reuse=True)(check_equally_long_as_first,)
    _sequences_list_length_equality_validator = pyd.validator(
        'sequences', allow_reuse=True)(check_equally_long_as_first,)
    _sorted_sequences_list_length_equality_validator = pyd.validator(
        'sorted_sequences', allow_reuse=True)(check_equally_long_as_first,)
    _name_length_pairs_list_length_equality_validator = pyd.validator(
        'name_length_pairs', allow_reuse=True)(check_equally_long_as_first,)


class SeqColLevel2Model(Model[SeqColLevel2Record]):
    ...
