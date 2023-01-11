from inspect import Parameter, signature
from typing import Optional, Type

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


class IterateFuncJobBaseMixin:
    # Requires FuncSignatureJobBaseMixin

    def __init__(self, *, iterate_over_data_files: bool = False):
        self._iterate_over_data_files = iterate_over_data_files

        if not isinstance(self.iterate_over_data_files, bool):
            raise TypeError(
                'Value of "iterate_over_data_files" parameter must be bool (True/False), '
                f'not "{iterate_over_data_files}"')

        if iterate_over_data_files:
            inner_func = self._job_func
            if inner_func.__name__ != '_omnipy_iterate_func':
                func_signature = signature(inner_func)
                params = list(func_signature.parameters.values())

                if len(params) == 0 or \
                        params[0].default != Parameter.empty or \
                        params[0].kind not in [Parameter.POSITIONAL_ONLY,
                                               Parameter.POSITIONAL_OR_KEYWORD]:
                    raise AttributeError(
                        'Parameter "iterate_over_data_files" is set to True,'
                        'but the job function has no arguments without default values. '
                        'The first argument will be replaced with a corresponding '
                        'Dataset arg to be iterated over')

                data_param = params[0]
                rest_params = params[1:]

                def create_dataset_cls(data_file_type: Type) -> Dataset[Model]:
                    return Dataset[data_file_type] if issubclass(data_file_type, Model) \
                        else Dataset[Model[data_file_type]]

                dataset_cls = create_dataset_cls(data_param.annotation)
                out_dataset_cls = create_dataset_cls(func_signature.return_annotation)
                dataset_param = data_param.replace(name='dataset', annotation=dataset_cls)
                new_signature = func_signature.replace(
                    parameters=[dataset_param] + rest_params,
                    return_annotation=out_dataset_cls,
                )

                def _omnipy_iterate_func(dataset: dataset_cls, *args: object, **kwargs: object):
                    out_dataset = out_dataset_cls()
                    for title, data_file in dataset.items():
                        out_dataset[title] = inner_func(data_file, *args, **kwargs)
                    return out_dataset

                self._job_func = _omnipy_iterate_func
                self._job_func.__signature__ = new_signature
                self._func_signature = new_signature
                self.__signature__ = new_signature

    @property
    def iterate_over_data_files(self) -> Optional[str]:
        return self._iterate_over_data_files
