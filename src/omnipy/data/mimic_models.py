from typing import Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from omnipy.data.model import _Model
    from omnipy.data.typedefs import KeyT, ValT, ValT2

    class Model_int(int, _Model[int]):
        ...

    class Model_float(_Model[float], float):
        ...

    class Model_bool(_Model[bool], bool):  # type: ignore[misc]
        ...

    class Model_str(_Model[str], str):  # type: ignore[misc]
        ...

    class Model_list(_Model[list[ValT]], list[ValT], Generic[ValT]):  # type: ignore[misc]
        ...

    class Model_tuple_all_same(_Model[tuple[ValT, ...]], tuple[ValT, ...], Generic[ValT]):
        ...

    class Model_tuple_pair(_Model[tuple[ValT, ValT2]], tuple[ValT, ValT2], Generic[ValT, ValT2]):
        ...

    class Model_dict(  # type: ignore[misc]
            _Model[dict[KeyT, ValT]],
            dict[KeyT, ValT],
            Generic[KeyT, ValT],
    ):
        ...
