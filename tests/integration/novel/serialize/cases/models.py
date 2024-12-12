from pydantic import BaseModel


class PydanticModel(BaseModel):
    number: int = 0
    string: str = ''


class TwoLevelPydanticModel(BaseModel):
    a: PydanticModel = PydanticModel()
    b: PydanticModel = PydanticModel()
