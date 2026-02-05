from omnipy.data.model import Model
import omnipy.util._pydantic as pyd


class NameLengthPair(pyd.BaseModel):
    name: str
    length: int


class SeqColLevel2Record(pyd.BaseModel):
    lengths: list[int]
    names: list[str]
    sequences: list[str]
    sorted_sequences: list[str]
    name_length_pairs: list[NameLengthPair]


class SeqColLevel2Model(Model[SeqColLevel2Record]):
    ...
