"""Storage backends for persisted job outputs: a local directory or S3-compatible storage.

Output persistence and restore use
[`get_output_storage`][omnipy.hub.output_storage.get_output_storage] to get the storage selected
by the output storage protocol. S3 support is built on ``fsspec`` and ``s3fs`` and needs the
``s3`` extra (``pip install omnipy[s3]``).

The S3 storage also offers plain file operations (upload, download, listing), used for example
by engines that stage job inputs in S3.
"""

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
import os
from pathlib import Path
import tempfile
from typing import Any, Protocol

from omnipy.shared.enums.job import OutputStorageProtocolOptions
from omnipy.shared.protocols.config import IsJobConfig, IsS3OutputStorageConfig


class IsOutputStorage(Protocol):
    """A directory tree for persisted outputs, addressed by '/'-separated relative paths."""

    @property
    def root(self) -> str:
        """Location of the storage root, for log messages."""
        ...

    def list_dirs(self, rel_path: str = '') -> list[str]:
        """Return the names of the directories in a directory, or an empty list if missing."""
        ...

    def list_files(self, rel_path: str = '') -> list[str]:
        """Return the names of the files in a directory, or an empty list if missing."""
        ...

    def write_bytes(self, rel_path: str, data: bytes | memoryview) -> None:
        """Write a file, creating parent directories as needed."""
        ...

    def local_copy(self, rel_path: str) -> AbstractContextManager[str]:
        """Context manager giving a local file path with the contents of a stored file."""
        ...


class LocalOutputStorage:
    """Persisted outputs in a local directory."""

    def __init__(self, root_dir: str | Path) -> None:
        self._root = Path(root_dir)

    @property
    def root(self) -> str:
        return str(self._root.absolute())

    def _entries(self, rel_path: str) -> list[Path]:
        path = self._root / rel_path
        return list(path.iterdir()) if path.is_dir() else []

    def list_dirs(self, rel_path: str = '') -> list[str]:
        return sorted(entry.name for entry in self._entries(rel_path) if entry.is_dir())

    def list_files(self, rel_path: str = '') -> list[str]:
        return sorted(entry.name for entry in self._entries(rel_path) if entry.is_file())

    def write_bytes(self, rel_path: str, data: bytes | memoryview) -> None:
        path = self._root / rel_path
        os.makedirs(path.parent, exist_ok=True)
        path.write_bytes(data)

    @contextmanager
    def local_copy(self, rel_path: str) -> Iterator[str]:
        yield str(self._root / rel_path)


def _import_fsspec() -> Any:
    try:
        import fsspec
    except ImportError as exc:  # pragma: no cover - fsspec comes with Prefect today
        raise ImportError(
            'S3 output storage needs the "s3" extra: pip install "omnipy[s3]"'
        ) from exc
    return fsspec


def s3_filesystem(s3_config: IsS3OutputStorageConfig) -> Any:
    """Return an fsspec file system for the S3 storage described by the config.

    Args:
        s3_config: S3 output storage config with endpoint URL and credentials.

    Returns:
        Any: An ``fsspec`` S3 file system.

    Raises:
        ImportError: If ``s3fs`` is not installed.
    """
    fsspec = _import_fsspec()
    options: dict[str, Any] = {}
    key = s3_config.access_key.get_secret_value()
    secret = s3_config.secret_key.get_secret_value()
    if key or secret:
        options |= {'key': key, 'secret': secret}
    if s3_config.endpoint_url:
        options['client_kwargs'] = {'endpoint_url': s3_config.endpoint_url}
    try:
        return fsspec.filesystem('s3', **options)
    except ImportError as exc:
        raise ImportError(
            'S3 output storage needs the "s3" extra: pip install "omnipy[s3]"'
        ) from exc


class FsspecOutputStorage:
    """Persisted outputs under a root path of an fsspec file system, such as an S3 bucket."""

    def __init__(self, filesystem: Any, root_path: str, protocol: str = 's3') -> None:
        self._fs = filesystem
        self._root_path = root_path.strip('/')
        self._protocol = protocol

    @property
    def root(self) -> str:
        return f'{self._protocol}://{self._root_path}'

    @property
    def filesystem(self) -> Any:
        """The underlying fsspec file system."""
        return self._fs

    def _path(self, rel_path: str) -> str:
        rel_path = rel_path.strip('/')
        return f'{self._root_path}/{rel_path}' if rel_path else self._root_path

    def _entries(self, rel_path: str, entry_type: str) -> list[str]:
        path = self._path(rel_path)
        if not self._fs.exists(path):
            return []
        return sorted(
            info['name'].rstrip('/').rsplit('/', 1)[-1]
            for info in self._fs.ls(path, detail=True)
            if info['type'] == entry_type
        )

    def list_dirs(self, rel_path: str = '') -> list[str]:
        return self._entries(rel_path, 'directory')

    def list_files(self, rel_path: str = '') -> list[str]:
        return self._entries(rel_path, 'file')

    def write_bytes(self, rel_path: str, data: bytes | memoryview) -> None:
        with self._fs.open(self._path(rel_path), 'wb') as file:
            file.write(bytes(data))

    @contextmanager
    def local_copy(self, rel_path: str) -> Iterator[str]:
        suffix = ''.join(Path(rel_path).suffixes)
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = os.path.join(tmp_dir, f'download{suffix}')
            self._fs.get(self._path(rel_path), local_path)
            yield local_path

    def upload_file(self, local_path: str | Path, rel_path: str) -> str:
        """Upload a local file and return its URL.

        Args:
            local_path: File to upload.
            rel_path: Destination, relative to the storage root.

        Returns:
            str: URL of the uploaded file, such as ``s3://bucket/prefix/file``.
        """
        self._fs.put(str(local_path), self._path(rel_path))
        return f'{self._protocol}://{self._path(rel_path)}'

    def download_file(self, rel_path: str, local_path: str | Path) -> None:
        """Download a file to a local path.

        Args:
            rel_path: File to download, relative to the storage root.
            local_path: Local destination path.
        """
        self._fs.get(self._path(rel_path), str(local_path))

    def download_dir(self, rel_path: str, local_dir: str | Path) -> None:
        """Download a directory recursively.

        Args:
            rel_path: Directory to download, relative to the storage root.
            local_dir: Local destination directory, created if needed.
        """
        os.makedirs(local_dir, exist_ok=True)
        self._fs.get(self._path(rel_path) + '/', str(local_dir), recursive=True)


def get_output_storage(
    job_config: IsJobConfig, protocol: OutputStorageProtocolOptions.Literals | None = None
) -> LocalOutputStorage | FsspecOutputStorage:
    """Return the output storage selected by a protocol, configured from the job config.

    Args:
        job_config: Job config holding the output storage settings.
        protocol: ``'local'`` or ``'s3'``. Defaults to the configured protocol.

    Returns:
        LocalOutputStorage | FsspecOutputStorage: The output storage.
    """
    output_storage = job_config.output_storage
    if protocol is None or protocol == OutputStorageProtocolOptions.FOLLOW_CONFIG:
        protocol = output_storage.protocol

    if protocol == OutputStorageProtocolOptions.S3:
        s3_config = output_storage.s3
        if not s3_config.bucket_name:
            raise ValueError(
                'S3 output storage needs a bucket name in the S3 output storage settings'
            )
        root_path = f'{s3_config.bucket_name}/{s3_config.persist_data_dir_path}'
        return FsspecOutputStorage(s3_filesystem(s3_config), root_path)

    return LocalOutputStorage(output_storage.local.persist_data_dir_path)
