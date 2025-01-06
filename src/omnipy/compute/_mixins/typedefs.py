from typing import Protocol, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

_InputT = TypeVar('_InputT', default=object)
_ModelInputT = TypeVar('_ModelInputT', bound=Model, default=Model)
_ReturnT = TypeVar('_ReturnT', default=object)
_ModelReturnT = TypeVar('_ModelReturnT', bound=Model, default=Model)
_InputTypeT: TypeAlias = _InputT | _ModelInputT
_InputDatasetT: TypeAlias = Dataset[Model[_InputT]] | Dataset[_ModelInputT]
_ReturnDatasetT: TypeAlias = Dataset[Model[_ReturnT]] | Dataset[_ModelReturnT]


class IsIterateInnerCallable(Protocol):
    """"""
    def __call__(
        self,
        data_file: _InputT | _ModelInputT,
        *args: object,
        **kwargs: object,
    ) -> _ReturnT | _ModelReturnT:
        ...

    __name__: str
