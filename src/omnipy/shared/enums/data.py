"""Data-related literal enums for retry and backoff behavior."""

from typing import Literal

from omnipy.util.literal_enum import LiteralEnum


class BackoffStrategy(LiteralEnum[str]):
    """Backoff strategy enum values for retry timing."""

    Literals = Literal['exponential', 'jitter', 'fibonacci', 'random']

    EXPONENTIAL: Literal['exponential'] = 'exponential'
    JITTER: Literal['jitter'] = 'jitter'
    FIBONACCI: Literal['fibonacci'] = 'fibonacci'
    RANDOM: Literal['random'] = 'random'
