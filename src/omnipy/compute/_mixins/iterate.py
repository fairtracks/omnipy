import asyncio
import functools
import inspect
from inspect import Parameter, signature
from typing import Any, Callable, cast, Coroutine

from omnipy.compute._mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute._mixins.typedefs import (_InputDatasetT,
                                             _InputTypeT,
                                             _ReturnDatasetT,
                                             IsIterateInnerCallable)
from omnipy.data.dataset import Dataset
from omnipy.data.helpers import FailedData, is_model_subclass, PendingData
from omnipy.data.model import Model
from omnipy.shared.protocols.compute._job import IsJobBase, IsPlainFuncArgJobBase
from omnipy.shared.protocols.data import IsDataset

# Functions


def _check_job_func_parameters(job_func: Callable) -> None:
    params = list(signature(job_func).parameters.values())

    if len(params) == 0 or \
            params[0].default != Parameter.empty or \
            params[0].kind not in [Parameter.POSITIONAL_ONLY,
                                   Parameter.POSITIONAL_OR_KEYWORD]:
        raise ValueError('Parameter "iterate_over_data_files" is set to True, '
                         'but the job function has no arguments without default values. '
                         'Such a first argument will be replaced with a corresponding '
                         'Dataset arg to be iterated over')


def _create_dataset_cls(data_file_type: _InputTypeT) -> type[IsDataset]:
    if is_model_subclass(data_file_type):
        return Dataset[data_file_type]  # type: ignore[valid-type]
    else:
        return Dataset[Model[data_file_type]]  # type: ignore[valid-type]


# Classes

# TODO: Data files -> data items throughout, e.g. iterate_over_data_items??

# TODO: Add a parameter to allow for "async for" iteration over data items, awaiting each
#       call of the underlying asynchronous function instead of running all calls concurrently,
#       as is currently implemented. This would be useful for cases where the processing of
#       each data item needs to be done sequentially, e.g. when the processing involves
#       modifying a shared resource that cannot be accessed concurrently. This would still
#       allow asynchronous processing of the job as a whole, e.g. in context of other jobs.


class IterateFuncJobBaseMixin:
    def __init__(  # noqa: C901
        self,
        *,
        iterate_over_data_files: bool = False,
        output_dataset_param: str | None = None,
        output_dataset_cls: type[IsDataset] | None = None,
    ):
        self_as_plain_func_arg_job_base = cast(IsPlainFuncArgJobBase, self)

        self._iterate_over_data_files = iterate_over_data_files
        self._input_dataset_type: type | None = None
        self._output_dataset_param = output_dataset_param
        self._output_dataset_cls = output_dataset_cls
        self._output_dataset_param_in_func: inspect.Parameter | None = None

        if not isinstance(self.iterate_over_data_files, bool):
            raise ValueError(
                'Value of "iterate_over_data_files" parameter must be bool (True/False), '
                f'not "{iterate_over_data_files}"')

        if not iterate_over_data_files:
            if output_dataset_param is not None:
                raise ValueError('Output dataset parameter can only be set when '
                                 '"iterate_over_data_files" is True')
            if output_dataset_cls is not None:
                raise ValueError(
                    'Output dataset class can only be set when "iterate_over_data_files" is True')

        if iterate_over_data_files:
            job_func = self_as_plain_func_arg_job_base._job_func
            if job_func.__name__ != '_omnipy_iterate_func':

                _check_job_func_parameters(job_func)
                self._generate_new_signature_for_iteration(job_func)

                def _sync_iterate_over_data_files_decorator(call_func: Callable):
                    def _omnipy_iterate_func(
                        dataset: _InputDatasetT,
                        *args: object,
                        **kwargs: object,
                    ) -> _ReturnDatasetT:
                        inner_func: IsIterateInnerCallable = \
                            cast(IsIterateInnerCallable, call_func)

                        output_dataset, args, kwargs = \
                            self._extract_output_dataset(dataset, *args, **kwargs)

                        for title, data_file in dataset.items():
                            data_arg = self._prepare_data_arg(data_file)
                            output_dataset[title] = inner_func(data_arg, *args, **kwargs)

                        return output_dataset

                    return _omnipy_iterate_func

                def _async_iterate_over_data_files_decorator(call_func: Callable):
                    async def _omnipy_iterate_func(
                        dataset: _InputDatasetT,
                        *args: object,
                        **kwargs: object,
                    ) -> _ReturnDatasetT:
                        inner_func: IsIterateInnerCallable = \
                            cast(IsIterateInnerCallable, call_func)

                        output_dataset, args, kwargs = \
                            self._extract_output_dataset(dataset, *args, **kwargs)

                        tasks = []
                        for title, data_file in dataset.items():
                            output_dataset[title] = self._create_pending_data()
                            data_arg = self._prepare_data_arg(data_file)
                            coro = cast(Coroutine, inner_func(data_arg, *args, **kwargs))

                            task = self._create_task(coro, output_dataset, title)
                            tasks.append(task)

                        await asyncio.gather(*tasks, return_exceptions=True)

                        return output_dataset

                    return _omnipy_iterate_func

                if inspect.iscoroutinefunction(job_func):
                    self_as_plain_func_arg_job_base._accept_call_func_decorator(
                        _async_iterate_over_data_files_decorator)
                else:
                    self_as_plain_func_arg_job_base._accept_call_func_decorator(
                        _sync_iterate_over_data_files_decorator)

    def _generate_new_signature_for_iteration(self, job_func: Callable) -> None:
        func_signature = signature(job_func)

        params = func_signature.parameters
        param_list = list(func_signature.parameters.values())
        input_data_param = param_list[0]
        rest_params = param_list[1:]

        self._input_dataset_type = input_data_param.annotation
        dataset_cls = _create_dataset_cls(self._input_dataset_type)
        dataset_param = input_data_param.replace(name='dataset', annotation=dataset_cls)

        if self._output_dataset_cls:
            output_dataset_cls = self._output_dataset_cls
        else:
            output_dataset_cls = _create_dataset_cls(func_signature.return_annotation)

        if self._output_dataset_param is not None:
            self._output_dataset_param_in_func = params.get(self._output_dataset_param, None)
            if inspect.iscoroutinefunction(job_func):
                if self._output_dataset_param_in_func:
                    raise ValueError(f'Output dataset parameter "{self._output_dataset_param}" '
                                     f'found in function signature for asynchronous job '
                                     f'"{job_func.__name__}". This is not allowed when '
                                     f'"iterate_over_data_files=True", as changing the dataset '
                                     f'within an async task in the middle of an async iteration '
                                     f'can easily cause concurrency issues.')

            if self._output_dataset_param_in_func:
                if self._output_dataset_param_in_func.annotation is not output_dataset_cls:
                    raise ValueError(f'Output dataset parameter "{self._output_dataset_param}" '
                                     f'found in function signature for synchronous job '
                                     f'"{job_func.__name__}" does not have the correct type '
                                     f'annotation. Expected "{output_dataset_cls}", but found '
                                     f'"{self._output_dataset_param_in_func.annotation}".')
            else:
                output_dataset_param = Parameter(
                    name=self._output_dataset_param,
                    kind=Parameter.KEYWORD_ONLY,
                    default=None,
                    annotation=output_dataset_cls,
                )
                rest_params = rest_params + [output_dataset_param]

        new_signature = func_signature.replace(
            parameters=[dataset_param] + rest_params,
            return_annotation=output_dataset_cls,
        )

        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)
        self_as_signature_func_job_base_mixin._update_func_signature(new_signature)

    def _extract_output_dataset(
        self,
        dataset: _InputDatasetT,
        *args: object,
        **kwargs: object,
    ) -> tuple[Dataset, tuple[object, ...], dict[str, object]]:
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)

        if self._output_dataset_param:
            if self._output_dataset_param_in_func and self._output_dataset_param not in kwargs:
                kwargs = kwargs.copy()
                kwargs[self._output_dataset_param] = cast(
                    Dataset, self_as_signature_func_job_base_mixin.return_type())

            bound_args = self_as_signature_func_job_base_mixin.get_bound_args(
                dataset, *args, **kwargs)
            output_dataset: Dataset | None = bound_args.arguments[self._output_dataset_param]

            return_args = bound_args.args[1:]
            return_kwargs = bound_args.kwargs
            if not self._output_dataset_param_in_func:
                return_kwargs.pop(self._output_dataset_param)
        else:
            output_dataset = None
            return_args = args
            return_kwargs = kwargs

        if output_dataset is None:
            output_dataset = cast(Dataset, self_as_signature_func_job_base_mixin.return_type())

        return output_dataset, return_args, return_kwargs

    def _prepare_data_arg(self, data_file):
        return data_file if is_model_subclass(self._input_dataset_type) else data_file.contents

    def _create_pending_data(self):
        self_as_job_base = cast(IsJobBase, self)
        return PendingData(
            job_name=self_as_job_base.name,
            job_unique_name=self_as_job_base.unique_name,
        )

    def _create_failed_data(self, exception: BaseException):
        self_as_job_base = cast(IsJobBase, self)
        return FailedData(
            job_name=self_as_job_base.name,
            job_unique_name=self_as_job_base.unique_name,
            exception=exception,
        )

    def _create_task(
        self,
        coro: Coroutine[_ReturnDatasetT, Any, Any],
        output_dataset: Dataset,
        title: str,
    ) -> asyncio.Task[_ReturnDatasetT]:
        def _done_callback(task: asyncio.Task, output_dataset: Dataset, title: str):
            if task.cancelled():
                output_dataset[title] = self._create_failed_data(RuntimeError('Task was cancelled'))
            else:
                exception = task.exception()
                if exception is not None:
                    output_dataset[title] = self._create_failed_data(exception)
                else:
                    try:
                        output_dataset[title] = task.result()
                    except Exception as e:
                        output_dataset[title] = self._create_failed_data(e)

        task = asyncio.create_task(coro)
        done_callback_for_title = functools.partial(
            _done_callback, output_dataset=output_dataset, title=title)
        task.add_done_callback(done_callback_for_title)

        return task

    @property
    def iterate_over_data_files(self) -> bool:
        return self._iterate_over_data_files

    @property
    def output_dataset_param(self) -> str | None:
        return self._output_dataset_param

    @property
    def output_dataset_cls(self) -> type[IsDataset] | None:
        return self._output_dataset_cls
