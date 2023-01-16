from typing import Protocol, Type, TypeVar, Union

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

InputT = TypeVar('InputT')
ModelInputT = TypeVar('ModelInputT', bound=Model)
ReturnT = TypeVar('ReturnT')
ModelReturnT = TypeVar('ModelReturnT', bound=Model)
InputTypeT = Union[Type[InputT], Type[ModelInputT]]
InputDatasetT = Union[Dataset[Type[Model[Type[InputT]]]], Dataset[Type[ModelInputT]]]
ReturnDatasetT = Union[Dataset[Type[Model[Type[ReturnT]]]], Dataset[Type[ModelReturnT]]]


class IsIterateInnerCallable(Protocol):
    def __call__(
        self,
        data_file: Union[InputT, ModelInputT],
        *args: object,
        **kwargs: object,
    ) -> Union[ReturnT, ModelReturnT]:
        ...

    __name__: str
