"""Helper functions for serializer tests."""

from io import BytesIO
from pathlib import Path
import tarfile


def write_tar_gz(path: Path, members: dict[str, bytes | None]) -> Path:
    """Write a gzipped tar archive with file members, or directory members for ``None``."""
    with tarfile.open(path, 'w:gz') as archive:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            if content is None:
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            else:
                info.size = len(content)
                archive.addfile(info, BytesIO(content))
    return path
