"""Datasets for HTTP URLs and automatically decoded HTTP response content."""

from omnipy.data.dataset import Dataset

from .models import AutoResponseContentModel, HttpUrlModel


class HttpUrlDataset(Dataset[HttpUrlModel]):
    """Store named HTTP or HTTPS URLs.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.dataset.Dataset`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.dataset.Dataset`.

    Returns:
        HttpUrlDataset: Dataset containing ``HttpUrlModel`` entries.

    Raises:
        TypeError: If provided values cannot be converted to ``HttpUrlModel``.

    Examples:
        >>> urls = HttpUrlDataset({'users': 'https://example.com/users'})
        >>> str(urls['users'])
        'https://example.com/users'
    """
    ...


class AutoResponseContentDataset(Dataset[AutoResponseContentModel]):
    """Store named HTTP responses decoded to JSON, text, or bytes.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.dataset.Dataset`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.dataset.Dataset`.

    Returns:
        AutoResponseContentDataset: Dataset containing ``AutoResponseContentModel`` entries.

    Raises:
        TypeError: If provided values cannot be converted to ``AutoResponseContentModel``.

    Examples:
        >>> responses = AutoResponseContentDataset({'a': b'data'})
        >>> 'a' in responses
        True
    """
    ...
