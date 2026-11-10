"""Datasets for host URLs and automatically decoded HTTP response content."""

from omnipy.data.dataset import Dataset

from .models import AutoResponseContentModel, HostUrlModel, HttpUrlModel


class HostUrlDataset(Dataset[HostUrlModel]):
    """Store named URLs using ``HostUrlModel`` without restricting their scheme.

    As with ``HostUrlModel``, URLs parsed without a host default to ``localhost``.
    The caller is responsible for choosing schemes appropriate for a host-based
    representation; scheme-specific semantics are not validated.

    Args:
        *args: Positional data forwarded to :class:`~omnipy.data.dataset.Dataset`.
        **kwargs: Keyword arguments forwarded to
            :class:`~omnipy.data.dataset.Dataset`.

    Returns:
        HostUrlDataset: Dataset containing ``HostUrlModel`` entries.

    Raises:
        pyd.ValidationError: If URL parsing fails.

    Examples:
        >>> urls = HostUrlDataset({'files': 'ftp://example.com/data'})
        >>> str(urls['files'])
        'ftp://example.com/data'
    """

    ...


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
