from typing import Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from omnipy.data.model import Model
    from omnipy.data.typedefs import KeyT, ValT, ValT2

    class Model_int(int, Model[int]):
        ...

    class Model_float(Model[float], float):
        ...

    class Model_bool(Model[bool], bool):  # type: ignore[misc]
        ...

    class Model_str(Model[str], str):  # type: ignore[misc]
        ...

    class Model_list(Model[list[ValT]], list[ValT], Generic[ValT]):  # type: ignore[misc]
        ...

    class Model_tuple_all_same(Model[tuple[ValT, ...]], tuple[ValT, ...], Generic[ValT]):
        ...

    class Model_tuple_pair(Model[tuple[ValT, ValT2]], tuple[ValT, ValT2], Generic[ValT, ValT2]):
        ...

    class Model_dict(  # type: ignore[misc]
            Model[dict[KeyT, ValT]],
            dict[KeyT, ValT],
            Generic[KeyT, ValT],
    ):
        ...
