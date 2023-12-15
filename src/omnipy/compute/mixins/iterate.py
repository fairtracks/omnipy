from inspect import Parameter, signature
from typing import Callable, cast, Type

from omnipy.api.protocols.private.compute.job import IsPlainFuncArgJobBase
from omnipy.compute.mixins.func_signature import SignatureFuncJobBaseMixin
from omnipy.compute.mixins.typedefs import (InputDatasetT,
                                            InputTypeT,
                                            IsIterateInnerCallable,
                                            ReturnDatasetT)
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

# Functions


def _check_job_func_parameters(job_func: Callable) -> None:
    params = list(signature(job_func).parameters.values())

    if len(params) == 0 or \
            params[0].default != Parameter.empty or \
            params[0].kind not in [Parameter.POSITIONAL_ONLY,
                                   Parameter.POSITIONAL_OR_KEYWORD]:
        raise AttributeError('Parameter "iterate_over_data_files" is set to True, '
                             'but the job function has no arguments without default values. '
                             'Such a first argument will be replaced with a corresponding '
                             'Dataset arg to be iterated over')


def _create_dataset_cls(data_file_type: InputTypeT) -> Type[InputDatasetT]:
    if issubclass(data_file_type, Model):
        return Dataset[data_file_type]  # type: ignore
    else:
        return Dataset[Model[data_file_type]]  # type: ignore


def _generate_new_signature(job_func: Callable):
    func_signature = signature(job_func)
    params = list(func_signature.parameters.values())
    data_param = params[0]
    rest_params = params[1:]

    dataset_cls = _create_dataset_cls(data_param.annotation)
    dataset_param = data_param.replace(name='dataset', annotation=dataset_cls)
    out_dataset_cls = _create_dataset_cls(func_signature.return_annotation)

    return func_signature.replace(
        parameters=[dataset_param] + rest_params,
        return_annotation=out_dataset_cls,
    )


# Classes


class IterateFuncJobBaseMixin:
    def __init__(self, *, iterate_over_data_files: bool = False):
        self_as_plain_func_arg_job_base = cast(IsPlainFuncArgJobBase, self)
        self_as_signature_func_job_base_mixin = cast(SignatureFuncJobBaseMixin, self)

        self._iterate_over_data_files = iterate_over_data_files

        if not isinstance(self.iterate_over_data_files, bool):
            raise TypeError(
                'Value of "iterate_over_data_files" parameter must be bool (True/False), '
                f'not "{iterate_over_data_files}"')

        if iterate_over_data_files:
            job_func = self_as_plain_func_arg_job_base._job_func
            if job_func.__name__ != '_omnipy_iterate_func':

                def _iterate_over_data_files_decorator(call_func: Callable):
                    def _omnipy_iterate_func(
                        dataset: InputDatasetT,
                        *args: object,
                        **kwargs: object,
                    ) -> ReturnDatasetT:
                        inner_func: IsIterateInnerCallable = \
                            cast(IsIterateInnerCallable, call_func)

                        return_type = signature(job_func).return_annotation
                        out_dataset_cls = _create_dataset_cls(return_type)
                        out_dataset = out_dataset_cls()

                        for title, data_file in dataset.items():
                            out_dataset[title] = inner_func(data_file.contents, *args, **kwargs)

                        return out_dataset

                    return _omnipy_iterate_func

                _check_job_func_parameters(job_func)
                self_as_plain_func_arg_job_base._accept_call_func_decorator(
                    _iterate_over_data_files_decorator)

                new_signature = _generate_new_signature(job_func)
                self_as_signature_func_job_base_mixin._update_func_signature(new_signature)

    @property
    def iterate_over_data_files(self) -> bool:
        return self._iterate_over_data_files
