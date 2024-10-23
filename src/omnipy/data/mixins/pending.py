from abc import ABC
from types import MethodType
from typing import Any, get_args, Iterable

from typing_extensions import TypeVar

from omnipy.api.exceptions import PendingDataError, ShouldNotOccurException
from omnipy.api.protocols.public.data import IsDataset
from omnipy.api.typedefs import TypeForm
from omnipy.data.helpers import is_model_subclass, PendingData
from omnipy.util.helpers import is_union

# ModelT = TypeVar('ModelT', bound=IsModel)
ModelT = TypeVar('ModelT')


class DatasetMixinBase(ABC):
    @classmethod
    def _clean_params(cls, params: TypeForm) -> TypeForm:
        return params

    @classmethod
    def _check_super_method_common(self, super_method: MethodType | None) -> MethodType | None:
        if super_method and callable(super_method):
            return super_method

    @classmethod
    def check_super_method_cls(cls, method_name: str) -> MethodType | None:
        super_method = getattr(super(), method_name, None)
        if cls._check_super_method_common(super_method):
            return super_method

    def check_super_method_self(self, method_name: str) -> MethodType | None:
        super_method = getattr(super(), method_name, None)
        if self._check_super_method_common(super_method):
            return super_method


class PendingDatasetMixin(DatasetMixinBase):
    def __class_getitem__(
        cls,
        params: type[ModelT] | tuple[type[ModelT], Any] | TypeVar | tuple[TypeVar, ...],
    ) -> 'type[IsDataset[type[ModelT]]]':
        super_class_getitem = cls.check_super_method_cls('__class_getitem__')
        if super_class_getitem:
            if is_model_subclass(params):
                dataset = super_class_getitem(params | PendingData)
                if params._get_root_field().allow_none:
                    dataset._get_data_field().allow_none = True
                return dataset
            else:
                return super_class_getitem(params)
        else:
            raise ShouldNotOccurException()

    @classmethod
    def _clean_params(
        cls,
        params: type[ModelT] | tuple[type[ModelT]] | tuple[type[ModelT], Any] | TypeVar
        | tuple[TypeVar, ...]
    ) -> type[ModelT] | tuple[type[ModelT], Any] | tuple[type[ModelT],
                                                         Any] | TypeVar | tuple[TypeVar, ...]:
        args = get_args(params)
        cleaned_params = args[0] if is_union(params) and len(
            args) == 2 and args[-1] is PendingData else params
        super_clean_params = cls.check_super_method_cls('_clean_params')
        if super_clean_params:
            return super_clean_params(cleaned_params)
        return cleaned_params

    def __getitem__(self, selector: str | int | slice | Iterable[str | int]) -> Any:
        super_getitem = self.check_super_method_self('__getitem__')
        if super_getitem:
            item = super_getitem(selector)
            if isinstance(item, PendingData):
                raise PendingDataError('Data is still pending')
        else:
            raise ShouldNotOccurException()

    @property
    def pending_data(self) -> IsDataset[type[ModelT]]:
        copy = self.__class__()
        copy.data = {key: val for key, val in self.data.items() if isinstance(val, PendingData)}
        return copy

    @property
    def available_data(self) -> IsDataset[type[ModelT]]:
        copy = self.__class__()
        copy.data = {key: val for key, val in self.data.items() if not isinstance(val, PendingData)}
        return copy

    def _check_value(self, value: Any) -> Any:
        if isinstance(value, PendingData):
            raise PendingDataError('Data is still pending')

        super_getvalue = self.check_super_method_self('_check_value')
        if super_getvalue:
            value = super_getvalue(value)

        return value
