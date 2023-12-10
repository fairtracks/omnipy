from typing import Protocol


class IsModifyContentsCallable(Protocol):
    """"""
    def __call__(self, data_file: str, **kwargs: object) -> str:
        ...


class IsModifyEachLineCallable(Protocol):
    """"""
    def __call__(self, line_no: int, line: str, **kwargs: object) -> str:
        ...


class IsModifyAllLinesCallable(Protocol):
    """"""
    def __call__(self, all_lines: list[str], **kwargs: object) -> list[str]:
        ...
