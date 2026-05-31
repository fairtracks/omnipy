"""Datasets for HTTP URLs and automatically decoded HTTP response content."""

from omnipy.data.dataset import Dataset

from .models import AutoResponseContentModel, HttpUrlModel


class HttpUrlDataset(Dataset[HttpUrlModel]):
    """Store named HTTP or HTTPS URLs."""
    ...


class AutoResponseContentDataset(Dataset[AutoResponseContentModel]):
    """Store named HTTP responses decoded to JSON, text, or bytes."""
    ...
