from typing import Generic, TYPE_CHECKING

from typing_extensions import Unpack

if TYPE_CHECKING:
    from omnipy.data._typedefs import _KeyT, _ValT, _ValTupleT
    from omnipy.data.model import Model

    class Model_int(Model[int], int):
        ...

    class Model_float(Model[float], float):
        ...

    class Model_bool(Model[bool], bool):  # type: ignore[misc]
        ...

    class Model_str(Model[str], str):  # type: ignore[misc]
        ...

    class Model_list(Model[list[_ValT]], list[_ValT], Generic[_ValT]):  # type: ignore[misc]
        ...

    class Model_tuple(  # type: ignore[misc]
            Model[tuple[Unpack[_ValTupleT]]],
            tuple[Unpack[_ValTupleT]],
            Generic[Unpack[_ValTupleT]],
    ):
        ...

    class Model_dict(  # type: ignore[misc]
            Model[dict[_KeyT, _ValT]],
            dict[_KeyT, _ValT],
            Generic[_KeyT, _ValT],
    ):
        ...
