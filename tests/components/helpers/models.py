from omnipy.util import pydantic as pyd


class Record(pyd.BaseModel):
    identity: object = None
    project: str = 'north'
    value: int = 0
