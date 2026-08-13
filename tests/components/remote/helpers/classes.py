"""Helper utilities for components remote tests."""

from dataclasses import dataclass

from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.compute.job import IsTaskTemplate


@dataclass
class EndpointCase:
    """Define EndpointCase."""
    query_urls: HttpUrlDataset
    auto_model_type: type[Model]


@dataclass
class RequestTypeCase:
    """Define RequestTypeCase."""
    is_async: bool
    job: IsTaskTemplate
    kwargs: dict[str, object]
    dataset_cls: type[Dataset]
    expected_exceptions: tuple[type[Exception], ...] | None = None
