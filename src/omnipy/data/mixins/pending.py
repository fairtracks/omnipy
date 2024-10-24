from typing import Any, get_args

from typing_extensions import TypeVar

from omnipy.api.exceptions import FailedDataError, PendingDataError
from omnipy.api.protocols.public.data import IsDataset
from omnipy.api.typedefs import TypeForm
from omnipy.data.helpers import FailedData, is_model_subclass, PendingData
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import is_union

# ModelT = TypeVar('ModelT', bound=IsModel)
ModelT = TypeVar('ModelT')
T = TypeVar('T')


class PendingDatasetMixin:
    @call_super_if_available(call_super_before_method=True)
    @classmethod
    def _prepare_params(cls, params: TypeForm) -> TypeForm:
        cleaned_params = cls._clean_model(params)
        if is_model_subclass(cleaned_params):
            return cleaned_params | PendingData | FailedData
        else:
            return cleaned_params

    @call_super_if_available(call_super_before_method=True)
    @classmethod
    def _clean_model(cls, model: TypeForm) -> TypeForm:
        args = get_args(model)
        if is_union(model) and len(args) == 3 and args[1:] == (PendingData, FailedData):
            return args[0]
        else:
            return model

    @property
    def pending_data(self) -> IsDataset[type[ModelT]]:
        copy = self.__class__()
        copy.data = {key: val for key, val in self.data.items() if isinstance(val, PendingData)}
        return copy

    @property
    def available_data(self) -> IsDataset[type[ModelT]]:
        copy = self.__class__()
        copy.data = {
            key: val for key,
            val in self.data.items() if not isinstance(val, (PendingData, FailedData))
        }
        return copy

    @property
    def failed_data(self) -> IsDataset[type[ModelT]]:
        copy = self.__class__()
        copy.data = {key: val for key, val in self.data.items() if isinstance(val, FailedData)}
        return copy

    @call_super_if_available(call_super_before_method=True)
    def _check_value(self, value: Any) -> Any:
        if isinstance(value, PendingData):
            raise PendingDataError(f'Dataset is still awaiting data from job "{value.job_name}"')
        elif isinstance(value, FailedData):
            raise FailedDataError(
                f'Job "{value.job_name}" failed to return data: {repr(value.exception)}')

        return value
