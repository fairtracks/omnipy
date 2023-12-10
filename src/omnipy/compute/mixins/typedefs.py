from typing import Protocol, TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

InputT = TypeVar('InputT', bound=object)
ModelInputT = TypeVar('ModelInputT', bound=Model)
ReturnT = TypeVar('ReturnT', bound=object)
ModelReturnT = TypeVar('ModelReturnT', bound=Model)
InputTypeT = InputT | ModelInputT
InputDatasetT = Dataset[Model[InputT]] | Dataset[ModelInputT]
ReturnDatasetT = Dataset[Model[ReturnT]] | Dataset[ModelReturnT]


class IsIterateInnerCallable(Protocol):
    """"""
    def __call__(
        self,
        data_file: InputT | ModelInputT,
        *args: object,
        **kwargs: object,
    ) -> ReturnT | ModelReturnT:
        ...

    __name__: str
