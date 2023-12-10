from collections import UserDict
from types import MappingProxyType
from typing import Generic, Sequence, TypeVar

_KeyT = TypeVar('_KeyT')
_ValT = TypeVar('_ValT')


# Unfortunately, MappingProxyType is declared as a final class, which means it cannot be subclassed.
# Inheriting from UserDict is a workaround.
class FrozenDict(UserDict[_KeyT, _ValT], Generic[_KeyT, _ValT]):
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
                 unfrozen_dict: dict[_KeyT, _ValT] | Sequence[tuple[_KeyT, _ValT]] | None = None,
                 /,
                 **kwargs):
        super().__init__(unfrozen_dict, **kwargs)
        self.data: MappingProxyType[_KeyT, _ValT] = MappingProxyType(self.data)  # type: ignore
