from typing import Annotated, NamedTuple

import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.components.raw.tasks import decode_bytes
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


def test_decode_bytes(runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    class DecodeCaseInfo(NamedTuple):
        bytes_data: bytes
        target_str: str
        encoding: str | None

    test_cases = [
        DecodeCaseInfo(b'', '', 'ascii'),
        DecodeCaseInfo(b'ASCII string', 'ASCII string', 'ascii'),
        DecodeCaseInfo(b'\xc3\xa6\xc3\xb8\xc3\xa5\xc3\x97\xe2\x80\xa0', 'æøå×†', 'utf-8'),
        DecodeCaseInfo(b'\xff\xfe\xe6\x00\xf8\x00\xe5\x00\xd7\x00  ', 'æøå×†', 'utf-16'),
        DecodeCaseInfo(b'\xd7 \xc6re v\xe6re \xf8let v\xe5rt! \xd7',
                       '× Ære være ølet vårt! ×',
                       'latin-1'),
        DecodeCaseInfo(b'\xd7 \xc6re v\xe6re \xf8let\x86 v\xe5rt! \xd7',
                       '× Ære være ølet† vårt! ×',
                       'windows-1252'),
    ]
    for case in test_cases:
        assert decode_bytes.run(
            Dataset[Model[bytes]](a=case.bytes_data), encoding=case.encoding)['a'].contents == \
            case.target_str

    for case in test_cases:
        assert decode_bytes.run(
            Dataset[Model[bytes]](a=case.bytes_data), encoding=None)['a'].contents == \
            case.target_str

    assert decode_bytes.run(
        Dataset[Model[bytes]](dict([(case.encoding, case.bytes_data) for case in test_cases])),
        encoding=None).to_data() == dict([(case.encoding, case.target_str) for case in test_cases])
