from typing import Protocol

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

InputT = TypeVar('InputT', default=object)
ModelInputT = TypeVar('ModelInputT', default=Model)
ReturnT = TypeVar('ReturnT', default=object)
ModelReturnT = TypeVar('ModelReturnT', default=Model)
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
