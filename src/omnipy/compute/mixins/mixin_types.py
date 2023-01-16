from typing import Protocol, Type, TypeVar, Union

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

InputT = TypeVar('InputT', bound=object)
ModelInputT = TypeVar('ModelInputT', bound=Model)
ReturnT = TypeVar('ReturnT', bound=object)
ModelReturnT = TypeVar('ModelReturnT', bound=Model)
InputTypeT = Union[InputT, ModelInputT]
InputDatasetT = Union[Dataset[Model[InputT]], Dataset[ModelInputT]]
ReturnDatasetT = Union[Dataset[Model[ReturnT]], Dataset[ModelReturnT]]


class IsIterateInnerCallable(Protocol):
    def __call__(
        self,
        data_file: Union[InputT, ModelInputT],
        *args: object,
        **kwargs: object,
    ) -> Union[ReturnT, ModelReturnT]:
        ...

    __name__: str
