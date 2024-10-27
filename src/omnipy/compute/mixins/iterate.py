import asyncio
import functools
import inspect
from inspect import Parameter, signature
from typing import Any, Callable, cast, Coroutine

from omnipy.api.protocols.private.compute.job import IsPlainFuncArgJobBase
from omnipy.api.protocols.public.data import IsDataset
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.typedefs import (InputDatasetT,
                                            InputTypeT,
                                            IsIterateInnerCallable,
                                            ReturnDatasetT)
from omnipy.data.dataset import Dataset
from omnipy.data.helpers import is_model_subclass, PendingData
from omnipy.data.model import Model

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


def _create_dataset_cls(data_file_type: InputTypeT) -> type[IsDataset]:
    if is_model_subclass(data_file_type):
        return Dataset[data_file_type]  # type: ignore[return-value, valid-type]
    else:
        return Dataset[Model[data_file_type]]  # type: ignore[return-value, valid-type]


def _create_task(
    coro: Coroutine[ReturnDatasetT, Any, Any],
    output_dataset: Dataset,
    title: str,
) -> asyncio.Task[ReturnDatasetT]:
    def _done_callback(task: asyncio.Task, output_dataset: Dataset, title: str):
        output_dataset[title] = task.result()

    task = asyncio.create_task(coro)
    done_callback_for_title = functools.partial(
        _done_callback, output_dataset=output_dataset, title=title)
    task.add_done_callback(done_callback_for_title)

    return task


# Classes


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
                        dataset: InputDatasetT,
                        *args: object,
                        **kwargs: object,
                    ) -> ReturnDatasetT:
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
                        dataset: InputDatasetT,
                        *args: object,
                        **kwargs: object,
                    ) -> ReturnDatasetT:
                        inner_func: IsIterateInnerCallable = \
                            cast(IsIterateInnerCallable, call_func)

                        output_dataset, args, kwargs = \
                            self._extract_output_dataset(dataset, *args, **kwargs)

                        tasks = []
                        for title, data_file in dataset.items():
                            output_dataset[title] = PendingData(job_name=job_func.__name__)
                            data_arg = self._prepare_data_arg(data_file)
                            coro = cast(Coroutine, inner_func(data_arg, *args, **kwargs))

                            task = _create_task(coro, output_dataset, title)
                            tasks.append(task)

                        await asyncio.gather(*tasks)

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
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
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
        dataset: InputDatasetT,
        *args: object,
        **kwargs: object,
    ) -> tuple[Dataset, tuple[object, ...], dict[str, object]]:
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)

        if self._output_dataset_param:
            bound_args = self_as_signature_func_job_base_mixin.get_bound_args(
                dataset, *args, **kwargs)
            output_dataset: Dataset = bound_args.arguments[self._output_dataset_param]

            if self._output_dataset_param_in_func:
                return_args = bound_args.args[1:]
            else:
                return_args = bound_args.args[1:-1]

            return output_dataset, return_args, bound_args.kwargs
        else:
            output_dataset = cast(Dataset, self_as_signature_func_job_base_mixin.return_type())
            return output_dataset, args, kwargs

    def _prepare_data_arg(self, data_file):
        return data_file if is_model_subclass(self._input_dataset_type) else data_file.contents

    @property
    def iterate_over_data_files(self) -> bool:
        return self._iterate_over_data_files

    @property
    def output_dataset_param(self) -> str | None:
        return self._output_dataset_param

    @property
    def output_dataset_cls(self) -> type[IsDataset] | None:
        return self._output_dataset_cls
