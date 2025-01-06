from typing import Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from omnipy.data._typedefs import _KeyT, _ValT, _ValT2
    from omnipy.data.model import Model

    class Model_int(int, Model[int]):
        ...

    class Model_float(Model[float], float):
        ...

    class Model_bool(Model[bool], bool):  # type: ignore[misc]
        ...

    class Model_str(Model[str], str):  # type: ignore[misc]
        ...

    class Model_list(Model[list[_ValT]], list[_ValT], Generic[_ValT]):  # type: ignore[misc]
        ...

    class Model_tuple_all_same(Model[tuple[_ValT, ...]], tuple[_ValT, ...], Generic[_ValT]):
        ...

    class Model_tuple_pair(Model[tuple[_ValT, _ValT2]],
                           tuple[_ValT, _ValT2],
                           Generic[_ValT, _ValT2]):
        ...

    class Model_dict(  # type: ignore[misc]
            Model[dict[_KeyT, _ValT]],
            dict[_KeyT, _ValT],
            Generic[_KeyT, _ValT],
    ):
        ...
