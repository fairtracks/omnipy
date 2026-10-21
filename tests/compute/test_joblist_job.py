"""Tests for the helpers shared by linear and DAG flows."""

import collections.abc
import inspect
import typing

import pytest

from omnipy.compute._joblist_job import ChildJobListArgJobBase

from .helpers.annotations import (
    GENERATOR_ANNOTATIONS,
    GENERATOR_LIKE_ANNOTATIONS,
    ITERATOR_ANNOTATIONS,
)

is_generator_like = ChildJobListArgJobBase._return_annotation_is_generator_like


@pytest.mark.parametrize(
    'annotation',
    GENERATOR_LIKE_ANNOTATIONS.values(),
    ids=GENERATOR_LIKE_ANNOTATIONS.keys(),
)
def test_bare_generator_like_annotations_are_detected(annotation: object) -> None:
    assert is_generator_like(annotation) is True


@pytest.mark.parametrize(
    'annotation',
    [
        typing.Generator[int, None, None],
        collections.abc.Generator[int, None, None],
        typing.AsyncGenerator[int, None],
        collections.abc.AsyncGenerator[int, None],
        typing.Iterator[int],
        collections.abc.Iterator[int],
        typing.AsyncIterator[int],
        collections.abc.AsyncIterator[int],
    ],
    ids=lambda annotation: str(annotation).replace('collections.abc.', 'abc.'),
)
def test_subscripted_generator_like_annotations_are_detected(annotation: object) -> None:
    assert is_generator_like(annotation) is True


@pytest.mark.parametrize(
    'annotation',
    GENERATOR_ANNOTATIONS.values(),
    ids=GENERATOR_ANNOTATIONS.keys(),
)
def test_generator_like_annotations_are_detected_when_nested(annotation: object) -> None:
    assert is_generator_like(list[annotation]) is True  # type: ignore[valid-type]
    assert is_generator_like(annotation | None) is True  # type: ignore[operator]
    assert is_generator_like(typing.Optional[annotation]) is True  # noqa: UP045


@pytest.mark.parametrize(
    'annotation',
    [
        int,
        str,
        None,
        list[int],
        dict[str, int],
        int | None,
        typing.Iterable[int],
        collections.abc.Iterable,
        collections.abc.Sequence,
        collections.abc.Awaitable,
        [],
        {},
        inspect.Signature.empty,
    ],
    ids=lambda annotation: getattr(annotation, '__name__', repr(annotation)),
)
def test_other_annotations_are_not_generator_like(annotation: object) -> None:
    assert is_generator_like(annotation) is False


def test_iterator_annotations_are_a_separate_group_from_generators() -> None:
    assert not set(ITERATOR_ANNOTATIONS) & set(GENERATOR_ANNOTATIONS)
