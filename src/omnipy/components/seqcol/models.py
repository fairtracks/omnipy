from typing import Any

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

# from omnipy.util.helpers import first_value_in_mapping


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
    def set_sorted_sequences(cls, v: list[str], values) -> list[str]:
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
                                values: dict[str, Any]) -> list[NameLengthPair]:
        if v:
            for i, name_length_pair in enumerate(v):
                assert name_length_pair.name == values['names'][i], \
                    (f'name_length_pairs[{i}].name must match names[{i}], '
                     f'{name_length_pair.name} != {values["names"][i]}')

                assert name_length_pair.length == values['lengths'][i], \
                    (f'name_length_pairs[{i}].length must match lengths[{i}], '
                     f'{name_length_pair.length} != {values["lengths"][i]}')
            return v
        else:
            return [
                NameLengthPair(name=name, length=length)
                for name, length in zip(values['names'], values['lengths'])
            ]

    # @pyd.validator(
    #     'names',
    #     'sequences',
    #     'sorted_sequences',
    #     'name_length_pairs',
    # )
    # def check_equal_length_lists(cls, v: list[Any], values: dict[str, Any]) -> dict[str, Any]:
    #     # Currently assumes that all fields are lists
    #     first_length = len(first_value_in_mapping(values))
    #     # assert all(len(val) == first_length for val in values.values()), \
    #     assert len(v) == first_length, \
    #         f'Length of fields must be equal: {({key:len(val) for key, val in values.items()})}'
    #     return values


class SeqColLevel2Model(Model[SeqColLevel2Record]):
    ...
