from typing import Any, cast, get_args

from typing_extensions import TypeVar

from omnipy.data.helpers import FailedData, HasData, is_model_subclass, PendingData
from omnipy.shared.exceptions import FailedDataError, PendingDataError
from omnipy.shared.protocols.data import IsDataset
from omnipy.shared.typedefs import TypeForm
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import is_union

# _ModelT = TypeVar('_ModelT', bound=IsModel)
_ModelT = TypeVar('_ModelT')


class TaskDatasetMixin:
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
    def available_data(self) -> IsDataset[type[_ModelT]]:
        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val
            for key, val in self_with_data.data.items()
            if not isinstance(val, (PendingData, FailedData))
        }
        return cast(IsDataset[type[_ModelT]], copy)

    @property
    def pending_data(self) -> IsDataset[type[_ModelT]]:
        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val for key, val in self_with_data.data.items() if isinstance(val, PendingData)
        }
        return cast(IsDataset[type[_ModelT]], copy)

    @property
    def failed_data(self) -> IsDataset[type[_ModelT]]:
        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val for key, val in self_with_data.data.items() if isinstance(val, FailedData)
        }
        return cast(IsDataset[type[_ModelT]], copy)

    def pending_task_details(self) -> dict[str, PendingData]:
        self_with_data = cast(HasData, self)
        return {
            key: val for key, val in self_with_data.data.items() if isinstance(val, PendingData)
        }

    def failed_task_details(self) -> dict[str, FailedData]:
        self_with_data = cast(HasData, self)
        return {key: val for key, val in self_with_data.data.items() if isinstance(val, FailedData)}

    @call_super_if_available(call_super_before_method=True)
    def _check_value(self, value: Any) -> Any:
        if isinstance(value, PendingData):
            raise PendingDataError(f'Dataset is still awaiting data from job "{value.job_name}"')
        elif isinstance(value, FailedData):
            raise FailedDataError(
                f'Job "{value.job_name}" failed to return data: {repr(value.exception)}'
            ) from value.exception

        return value
