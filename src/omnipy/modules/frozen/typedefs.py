from collections import UserDict
from types import MappingProxyType
from typing import Generic, Hashable, Sequence

from typing_extensions import TypeVar

from ..general.models import NotIterableExceptStrOrBytesModel

KeyT = TypeVar('KeyT', default=str | Hashable)
ValT = TypeVar(
    'ValT', bound=NotIterableExceptStrOrBytesModel, default=NotIterableExceptStrOrBytesModel)


# Unfortunately, MappingProxyType is declared as a final class, which means it cannot be subclassed.
# Inheriting from UserDict is a workaround.
class FrozenDict(UserDict[KeyT, ValT], Generic[KeyT, ValT]):
    """
    FrozenDict works exactly like a dict except that it cannot be modified after initialisation:

        >>> from omnipy import FrozenDict, print_exception
        >>> from types import MappingProxyType
        >>>
        >>> my_dict = FrozenDict({'temperature': 'chilly'})
        >>> my_dict
        mappingproxy({'temperature': 'chilly'})
        >>> my_dict['temperature']
        'chilly'
        >>> with print_exception:
        ...     my_dict['temperature'] = 'scorching'
        TypeError: 'mappingproxy' object does not support item assignment

    In contrast to types.MappingProxyType, FrozenDict can be initialized without parameters:

        >>> with print_exception:
        ...     MappingProxyType()
        TypeError: mappingproxy() missing required argument 'mapping' (pos 1)
        >>> FrozenDict()
        mappingproxy({})

    Typically, this would be a rather useless thing to do, as the resulting object would be an empty
    dictionary that cannot be changed. With Omnipy it actually makes sense, though, as the Model
    class calls the type argument without parameters to determine the default value of the model.

    Note:
        Mutable objects within a FrozenDict are still mutable:

        >>> my_dict = FrozenDict({'temp_map': {'cold': 'chilly', 'hot': 'scorching'}})
        >>> my_dict['temp_map']['hot'] = 'blazing'
        >>> my_dict
        mappingproxy({'temp_map': {'cold': 'chilly', 'hot': 'blazing'}})

        To implement a fully immutable nested data structure, one would need a mechanism that makes
        sure only immutable types are allowed within a FrozenDict (or a tuple, which is the
        immutable list counterpart). Luckily, Omnipy provides just that guarantee with
        NestedFrozenDictsModel, NestedTuplesModel and NestedFrozenCollectionsModel.
    """
    def __init__(self,
                 unfrozen_dict: dict[KeyT, ValT] | Sequence[tuple[KeyT, ValT]] | None = None,
                 /,
                 **kwargs):
        super().__init__(unfrozen_dict, **kwargs)
        self.data: MappingProxyType[KeyT, ValT] = MappingProxyType(self.data)  # type: ignore

    def __repr__(self):
        return f"{self.__class__.__name__}({self.data if hasattr(self, 'data') else ''})"
