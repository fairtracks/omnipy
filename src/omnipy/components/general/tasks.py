import os
from typing import Type, TypeVar

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

# @TaskTemplate()
# def cast_dataset(dataset: Dataset, cast_model: Callable[[], _ModelT]) -> _ModelT:
#     out_dataset: Dataset[_ModelT] = Dataset[cast_model]()
#     for name, item in dataset.items():
#         out_dataset[name] = cast(cast_model, item.to_data())
#     return out_dataset


@TaskTemplate()
def split_dataset(
        dataset: Dataset[Model[object]],
        datafile_names_for_b: list[str]) -> tuple[Dataset[Model[object]], Dataset[Model[object]]]:
    model_cls = dataset.get_model_class()
    datafile_names_for_a = set(dataset.keys()) - set(datafile_names_for_b)
    dataset_a = Dataset[model_cls](  # type: ignore
        {
            name: dataset[name] for name in dataset.keys() if name in datafile_names_for_a
        })
    dataset_b = Dataset[model_cls](  # type: ignore
        {
            name: dataset[name] for name in dataset.keys() if name in datafile_names_for_b
        })
    return dataset_a, dataset_b


@TaskTemplate()
def import_directory(directory: str,
                     exclude_prefixes: tuple[str, ...] = ('.', '_'),
                     include_suffixes: tuple[str, ...] = (),
                     model: Type[Model] = Model[str]) -> Dataset[Model]:
    dataset = Dataset[model]()
    for import_filename in os.listdir(directory):
        if not exclude_prefixes or \
                not any(import_filename.startswith(prefix) for prefix in exclude_prefixes):
            if not include_suffixes or \
                    any(import_filename.endswith(suffix) for suffix in include_suffixes):
                with open(os.path.join(directory, import_filename)) as open_file:
                    dataset_name = '_'.join(import_filename.split('.')[:-1])
                    print(f"{import_filename} -> Dataset['{dataset_name}']")
                    dataset[dataset_name] = open_file.read()
    return dataset


_DatasetT = TypeVar('_DatasetT', bound=Dataset)


@TaskTemplate()
def convert_dataset(dataset: Dataset, dataset_cls: type[_DatasetT], **kwargs: object) -> _DatasetT:
    return dataset_cls(dataset, **kwargs)
