from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..helpers.classes import (
    DisplayRecord,
    IntegerDataset,
    MergedRecordDataset,
    WrappedDatasetCase,
    WrappedIntegerDataset,
)


def case_direct_wrapper() -> WrappedDatasetCase:
    dataset = Dataset[Model[int]](first=1, second=2)
    return WrappedDatasetCase(wrapped=Model[Dataset[Model[int]]](dataset), dataset=dataset)


def case_subclass_wrapper() -> WrappedDatasetCase:
    dataset = IntegerDataset(first=1, second=2)
    return WrappedDatasetCase(wrapped=WrappedIntegerDataset(dataset), dataset=dataset)


def case_nested_wrapper() -> WrappedDatasetCase:
    dataset = IntegerDataset(first=1, second=2)
    return WrappedDatasetCase(wrapped=Model[WrappedIntegerDataset](dataset), dataset=dataset)


def case_union_wrapper() -> WrappedDatasetCase:
    dataset = IntegerDataset(first=1, second=2)
    return WrappedDatasetCase(wrapped=Model[IntegerDataset | int](dataset), dataset=dataset)


def case_nested_union_wrapper() -> WrappedDatasetCase:
    dataset = IntegerDataset(first=1, second=2)
    return WrappedDatasetCase(
        wrapped=Model[Model[WrappedIntegerDataset | str] | int](dataset), dataset=dataset
    )


def case_merged_record_pages() -> WrappedDatasetCase:
    first = DisplayRecord(name='first', value=1)
    second = DisplayRecord(name='second', value=2)
    return WrappedDatasetCase(
        wrapped=MergedRecordDataset({'page': [first, second]}),
        dataset=Dataset[Model[DisplayRecord]](first=first, second=second),
    )
