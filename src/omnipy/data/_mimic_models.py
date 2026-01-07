from typing import Any, Generic, TypeVar

from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING

if TYPE_CHECKING:

    from omnipy.data._typedefs import _KeyT, _ValT, _ValT2
    from omnipy.data.dataset import _ModelOrDatasetT, Dataset
    from omnipy.data.model import Model
    from omnipy.shared.protocols.builtins import IsDict, IsList, IsPairTuple, IsSameTypeTuple
    from omnipy.shared.protocols.data import IsDataset, IsModel

    class Model_int(Model[int], int):
        ...

    class Model_float(Model[float], float):
        ...

    class Model_bool(Model[bool], bool):
        ...

    class Model_str(Model[str], str):
        ...

    class Model_list(  # type: ignore[misc]
            IsList[_ValT],
            Model[list[_ValT]],
            Generic[_ValT],
    ):
        ...

    class Model_tuple_same_type(  # type: ignore[misc]
            IsSameTypeTuple[_ValT],
            Model[tuple[_ValT, ...]],
            Generic[_ValT],
    ):
        ...

    class Model_tuple_pair(  # type: ignore[misc]
            IsPairTuple[_ValT, _ValT2],
            Model[tuple[_ValT, _ValT2]],
            Generic[_ValT, _ValT2]):
        ...

    class Model_dict(  # type: ignore[misc]
            IsDict[_KeyT, _ValT],
            Model[dict[_KeyT, _ValT]],
            Generic[_KeyT, _ValT],
    ):
        ...

    class Model_Dataset(  # type: ignore[misc]
            IsDataset[_ModelOrDatasetT],  # type: ignore[misc]
            Model[Dataset[_ModelOrDatasetT]],
            Generic[_ModelOrDatasetT],
    ):
        ...

    _CorrectModelT = TypeVar('_CorrectModelT', bound=IsModel)

    class RevertModelMimicTypingHack(Generic[_CorrectModelT]):
        # Need to override Model.__new__() hack for Pyright to correctly
        # handle subclassing when one of the Mimic models is used as a base
        # class.

        if TYPE_CHECKER != 'mypy':

            def __new__(cls, *args: Any, **kwargs: Any) -> _CorrectModelT:
                ...
