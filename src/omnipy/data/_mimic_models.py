from typing import Generic, TYPE_CHECKING

if TYPE_CHECKING:

    from omnipy.data._typedefs import _KeyT, _ValT, _ValT2
    from omnipy.data.model import Model
    from omnipy.shared.protocols.builtins import IsDict, IsList, IsPairTuple, IsSameTypeTuple

    class Model_int(Model[int], int):
        ...

    class Model_float(Model[float], float):
        ...

    class Model_bool(Model[bool], bool):  # type: ignore[misc]
        ...

    class Model_str(Model[str], str):  # type: ignore[misc]
        ...

    class Model_list(IsList[_ValT], Model[list[_ValT]], Generic[_ValT]):
        ...

    class Model_tuple_same_type(IsSameTypeTuple[_ValT], Model[tuple[_ValT, ...]], Generic[_ValT]):
        ...

    class Model_tuple_pair(IsPairTuple[_ValT, _ValT2],
                           Model[tuple[_ValT, _ValT2]],
                           Generic[_ValT, _ValT2]):
        ...

    class Model_dict(
            IsDict[_KeyT, _ValT],
            Model[dict[_KeyT, _ValT]],
            Generic[_KeyT, _ValT],
    ):
        ...
