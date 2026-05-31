"""Task-state dataset helpers used by Omnipy task-producing datasets."""

from typing import Any, cast, get_args

from typing_extensions import Self

from omnipy.data.helpers import FailedData, PendingData
from omnipy.shared.exceptions import FailedDataError, PendingDataError
from omnipy.shared.protocols.data import HasData, IsFailedData, IsPendingData
from omnipy.shared.typedefs import TypeForm
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import is_union


class TaskDatasetMixin:
    """Add pending/failed task state handling to dataset-like classes.

    Omnipy uses this mixin for datasets whose entries may temporarily hold ``PendingData`` or
    ``FailedData`` markers instead of final model values. The mixin provides filtered views and
    metadata extraction helpers for those task-oriented datasets.
    """
    @call_super_if_available(call_super_before_method=True)
    @classmethod
    def _prepare_params(cls, params: TypeForm) -> TypeForm:
        from omnipy.data.model import is_model_subclass

        cleaned_params = cls._clean_type(params)
        if is_model_subclass(cleaned_params):
            return cleaned_params | PendingData | FailedData
        else:
            return cleaned_params

    @call_super_if_available(call_super_before_method=True)
    @classmethod
    def _clean_type(cls, _type: TypeForm) -> TypeForm:
        args = get_args(_type)
        if is_union(_type) and len(args) == 3 and args[1:] == (PendingData, FailedData):
            return args[0]
        else:
            return _type

    @property
    def available_data(self) -> Self:
        """Return a same-type copy containing only successfully available data entries."""

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
        """Return a same-type copy containing only entries still waiting on task results."""

        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val for key, val in self_with_data.data.items() if isinstance(val, PendingData)
        }
        return cast(Self, copy)

    @property
    def failed_data(self) -> Self:
        """Return a same-type copy containing only entries whose producing task failed."""

        self_with_data = cast(HasData, self)
        copy = cast(HasData, self.__class__())
        copy.data = {
            key: val for key, val in self_with_data.data.items() if isinstance(val, FailedData)
        }
        return cast(Self, copy)

    def pending_task_details(self) -> dict[str, IsPendingData]:
        """Return pending task marker payloads keyed by dataset entry name."""

        self_with_data = cast(HasData, self)
        return {  # pyright: ignore [reportReturnType]
            key: val for key, val in self_with_data.data.items() if isinstance(val, PendingData)
        }

    def failed_task_details(self) -> dict[str, IsFailedData]:
        """Return failure marker payloads keyed by dataset entry name."""

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
