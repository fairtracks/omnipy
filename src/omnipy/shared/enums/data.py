"""Data-related literal enums for retry and backoff behavior and serializer selection."""

from typing import Literal

from omnipy.util.literal_enum import LiteralEnum


class BackoffStrategy(LiteralEnum[str]):
    """Backoff strategy enum values for retry timing."""

    Literals = Literal['exponential', 'jitter', 'fibonacci', 'random']

    EXPONENTIAL: Literal['exponential'] = 'exponential'
    JITTER: Literal['jitter'] = 'jitter'
    FIBONACCI: Literal['fibonacci'] = 'fibonacci'
    RANDOM: Literal['random'] = 'random'


class SelectSerializerBy(LiteralEnum[str]):
    """How to select serializers when loading local files.

    With ``TYPE``, serializers are first selected by the type of the target, reading all files
    regardless of their suffixes. If no serializer supports the target type, selection falls
    back to ``SUFFIX``. With ``SUFFIX``, serializers are selected by the file suffixes. If no
    serializer supports the file suffix, the files are read as raw bytes. As a single serializer
    is selected for all files, files with different suffixes raise an error.
    """

    Literals = Literal['type', 'suffix']

    TYPE: Literal['type'] = 'type'
    SUFFIX: Literal['suffix'] = 'suffix'
