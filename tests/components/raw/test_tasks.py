"""Tests for raw component tasks."""

from typing import Annotated, NamedTuple

import pytest

from omnipy.components.raw.tasks import (concat_all_args,
                                         concat_all_kwargs,
                                         decode_bytes,
                                         union_all_args,
                                         union_all_kwargs)
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.shared.protocols.hub.runtime import IsRuntime


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
        DecodeCaseInfo(b'\xc6re v\xe6re \xf8let v\xe5rt!', 'Ære være ølet vårt!', 'latin-1'),
        DecodeCaseInfo(b'\xc6re v\xe6re \xf8let\x86 v\xe5rt!',
                       'Ære være ølet† vårt!',
                       'windows-1252'),
    ]
    for case in test_cases:
        assert decode_bytes.run(
            Dataset[Model[bytes]](a=case.bytes_data), encoding=case.encoding)['a'].content == \
            case.target_str

    for case in test_cases:
        assert decode_bytes.run(
            Dataset[Model[bytes]](a=case.bytes_data), encoding=None)['a'].content == \
            case.target_str

    assert decode_bytes.run(
        Dataset[Model[bytes]](dict([(case.encoding, case.bytes_data) for case in test_cases])),
        encoding=None).to_data() == dict([(case.encoding, case.target_str) for case in test_cases])


def test_concat_all_args_accepts_positional_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[list[int]]](a=[1], b=[2])
    middle_dataset = Dataset[Model[list[int]]](c=[3])
    right_dataset = Dataset[Model[list[int]]](d=[4])

    assert concat_all_args.run(left_dataset, middle_dataset,
                               right_dataset).to_data() == [1, 2, 3, 4]


def test_concat_all_kwargs_accepts_named_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[list[int]]](a=[1], b=[2])
    middle_dataset = Dataset[Model[list[int]]](c=[3])
    right_dataset = Dataset[Model[list[int]]](d=[4])

    assert concat_all_kwargs.run(
        left=left_dataset, middle=middle_dataset, right=right_dataset).to_data() == [1, 2, 3, 4]


def test_union_all_kwargs_accepts_named_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[dict[str, int]]](a={'a': 1})
    middle_dataset = Dataset[Model[dict[str, int]]](b={'b': 2})
    right_dataset = Dataset[Model[dict[str, int]]](c={'c': 3})

    assert union_all_kwargs.run(
        left=left_dataset,
        middle=middle_dataset,
        right=right_dataset,
    ).to_data() == {
        'a': 1,
        'b': 2,
        'c': 3,
    }


def test_union_all_args_accepts_positional_datasets(
        runtime: Annotated[IsRuntime, pytest.fixture]) -> None:
    left_dataset = Dataset[Model[dict[str, int]]](a={'a': 1})
    middle_dataset = Dataset[Model[dict[str, int]]](b={'b': 2})
    right_dataset = Dataset[Model[dict[str, int]]](c={'c': 3})

    assert union_all_args.run(left_dataset, middle_dataset, right_dataset).to_data() == {
        'a': 1,
        'b': 2,
        'c': 3,
    }
