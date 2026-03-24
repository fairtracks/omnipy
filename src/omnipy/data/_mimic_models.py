from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Generic

    from typing_extensions import TypeVar

    from omnipy.data._typedefs import _KeyT, _ValT, _ValT2
    from omnipy.data.dataset import _ModelOrDatasetT, Dataset
    from omnipy.data.model import PlainModel
    from omnipy.shared.protocols.builtins import IsBool, IsFloat, IsInt
    from omnipy.shared.protocols.content import (IsBytesContent,
                                                 IsDictContent,
                                                 IsListContent,
                                                 IsPairTupleContent,
                                                 IsSameTypeTupleContent,
                                                 IsStrContent)
    from omnipy.shared.protocols.data import IsDataset, IsModel

    class Model_int(PlainModel[int], IsInt):
        ...

    class Model_float(PlainModel[float], IsFloat):
        ...

    class Model_bool(PlainModel[bool], IsBool):
        ...

    class Model_str(PlainModel[str], IsStrContent):
        ...

    class Model_bytes(PlainModel[bytes], IsBytesContent):
        ...

    class Model_list(  # type: ignore[misc]
            PlainModel[list[_ValT]],
            IsListContent[_ValT],
            Generic[_ValT],
    ):
        ...

    class Model_tuple_same_type(  # type: ignore[misc]
            PlainModel[tuple[_ValT, ...]],
            IsSameTypeTupleContent[_ValT],
            Generic[_ValT],
    ):
        ...

    class Model_tuple_pair(  # type: ignore[misc]
            PlainModel[tuple[_ValT, _ValT2]],
            IsPairTupleContent[_ValT, _ValT2],
            Generic[_ValT, _ValT2],
    ):
        ...

    class Model_dict(  # type: ignore[misc]
            PlainModel[dict[_KeyT, _ValT]],
            IsDictContent[_KeyT, _ValT],
            Generic[_KeyT, _ValT],
    ):
        ...

    class Model_Dataset(  # type: ignore[misc]
            PlainModel[Dataset[_ModelOrDatasetT]],
            IsDataset[_ModelOrDatasetT],
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
