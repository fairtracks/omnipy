"""TYPE_CHECKING-only model facades used to improve static typing behavior.

Type Aliases:
    The mimic model classes in this module mirror common ``Model[...]`` shapes so
    type checkers can reason about container-specialized content more precisely.
"""

import os
from textwrap import dedent

from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING
from omnipy.util.helpers import is_package_editable


if is_package_editable('omnipy'):  # Only define environment variables when developing
    os.environ['OMNIPY_MACRO_MIMIC_MODEL_TYPED_STANDIN_SUMMARY'] = dedent("""\
        Typed stand-in for a concrete ``Model[...]`` subclass.
    """)

if TYPE_CHECKING:
    from typing import Any, Generic

    from typing_extensions import Self, TypeVar

    from omnipy.data._typing.typedefs import _KeyT, _ValT, _ValT2
    from omnipy.data.dataset import _ModelOrDatasetT, Dataset
    from omnipy.data.model import Model
    from omnipy.shared.protocols.content import (IsBoolContent,
                                                 IsBytesContent,
                                                 IsDictContent,
                                                 IsFloatContent,
                                                 IsIntContent,
                                                 IsListContent,
                                                 IsPairTupleContent,
                                                 IsSameTypeTupleContent,
                                                 IsSetContent,
                                                 IsStrContent)
    from omnipy.shared.protocols.data import IsDataset, IsModel

    _RootT = TypeVar('_RootT')

    class PlainModel(
            Model[_RootT],
            Generic[_RootT],
    ):
        """Minimal generic stand-in for ``Model[_RootT]`` during type checking."""

        if TYPE_CHECKER != 'mypy':

            def __new__(cls, *args: Any, **kwargs: Any) -> Self:
                ...

    class Model_int(PlainModel[int], IsIntContent):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_float(PlainModel[float], IsFloatContent):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_bool(PlainModel[bool], IsBoolContent):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_str(PlainModel[str], IsStrContent):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_bytes(PlainModel[bytes], IsBytesContent):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_set(  # type: ignore[misc]
            PlainModel[set[_ValT]],
            IsSetContent[_ValT],
            Generic[_ValT],
    ):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_list(  # type: ignore[misc]
            PlainModel[list[_ValT]],
            IsListContent[_ValT],
            Generic[_ValT],
    ):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_tuple_same_type(  # type: ignore[misc]
            PlainModel[tuple[_ValT, ...]],
            IsSameTypeTupleContent[_ValT],
            Generic[_ValT],
    ):
        """Typed stand-in for homogeneous tuple models."""

        ...

    class Model_tuple_pair(  # type: ignore[misc]
            PlainModel[tuple[_ValT, _ValT2]],
            IsPairTupleContent[_ValT, _ValT2],
            Generic[_ValT, _ValT2],
    ):
        """Typed stand-in for two-element tuple models."""

        ...

    class Model_dict(  # type: ignore[misc]
            PlainModel[dict[_KeyT, _ValT]],
            IsDictContent[_KeyT, _ValT],
            Generic[_KeyT, _ValT],
    ):
        """{{MIMIC_MODEL_TYPED_STANDIN_SUMMARY}}"""

        ...

    class Model_Dataset(  # type: ignore[misc]
            PlainModel[Dataset[_ModelOrDatasetT]],
            IsDataset[_ModelOrDatasetT],
            Generic[_ModelOrDatasetT],
    ):
        """Typed stand-in for dataset-valued models."""

        ...

    _CorrectModelT = TypeVar('_CorrectModelT', bound=IsModel)

    class RevertModelMimicTypingHack(Generic[_CorrectModelT]):
        """Restore normal subclass typing when mimic models are used as bases."""

        # Need to override Model.__new__() hack for Pyright to correctly
        # handle subclassing when one of the Mimic models is used as a base
        # class.

        if TYPE_CHECKER != 'mypy':

            def __new__(cls, *args: Any, **kwargs: Any) -> _CorrectModelT:
                ...
