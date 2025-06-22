from typing import Any, cast, get_args

from typing_extensions import Self

from omnipy.data.helpers import FailedData, PendingData
from omnipy.data.typechecks import is_model_subclass
from omnipy.shared.exceptions import FailedDataError, PendingDataError
from omnipy.shared.protocols.data import HasData, IsFailedData, IsPendingData
from omnipy.shared.typedefs import TypeForm
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import is_union


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
    def available_data(self) -> Self:
        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val
            for key, val in self_with_data.data.items()
            if not isinstance(val, (PendingData, FailedData))
        }
        return cast(Self, copy)

    @property
    def pending_data(self) -> Self:
        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val for key, val in self_with_data.data.items() if isinstance(val, PendingData)
        }
        return cast(Self, copy)

    @property
    def failed_data(self) -> Self:
        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val for key, val in self_with_data.data.items() if isinstance(val, FailedData)
        }
        return cast(Self, copy)

    def pending_task_details(self) -> dict[str, IsPendingData]:
        self_with_data = cast(HasData, self)
        return {  # pyright: ignore [reportReturnType]
            key: val for key, val in self_with_data.data.items() if isinstance(val, PendingData)
        }

    def failed_task_details(self) -> dict[str, IsFailedData]:
        self_with_data = cast(HasData, self)
        return {  # pyright: ignore [reportReturnType]
            key: val for key, val in self_with_data.data.items() if isinstance(val, FailedData)
        }

    @call_super_if_available(call_super_before_method=True)
    def _check_value(self, value: Any) -> Any:
        if isinstance(value, PendingData):
            raise PendingDataError(f'Dataset is still awaiting data from job "{value.job_name}"')
        elif isinstance(value, FailedData):
            raise FailedDataError(
                f'Job "{value.job_name}" failed to return data: {repr(value.exception)}'
            ) from value.exception

        return value
