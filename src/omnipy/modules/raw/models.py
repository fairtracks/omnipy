import os

from omnipy.data.model import Model


class SplitLinesModel(Model[str | list[str]]):
    @classmethod
    def _parse_data(cls, data: str | list[str]) -> list[str]:
        if isinstance(data, list):
            return data
        return data.split(os.linesep)


class SplitAndStripLinesModel(SplitLinesModel):
    @classmethod
    def _parse_data(cls, data: str | list[str]) -> list[str]:
        return [line.strip() for line in super()._parse_data(data)]


class JoinLinesModel(Model[list[str] | str]):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> str:
        if isinstance(data, str):
            return data
        return os.linesep.join(data)
