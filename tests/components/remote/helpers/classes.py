"""Helper utilities for components remote tests."""

from dataclasses import dataclass

from omnipy import Dataset, HttpUrlDataset, Model, TaskTemplate


@dataclass
class EndpointCase:
    """Define EndpointCase."""
    query_urls: HttpUrlDataset
    auto_model_type: type[Model]


@dataclass
class RequestTypeCase:
    """Define RequestTypeCase."""
    is_async: bool
    job: TaskTemplate
    kwargs: dict[str, object]
    dataset_cls: type[Dataset]
    expected_exceptions: tuple[type[Exception], ...] | None = None
