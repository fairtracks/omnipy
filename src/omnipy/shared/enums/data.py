from typing import Literal

from omnipy.util.literal_enum import LiteralEnum


class BackoffStrategy(LiteralEnum[str]):
    Literals = Literal['exponential', 'jitter', 'fibonacci', 'random']

    EXPONENTIAL: Literal['exponential'] = 'exponential'
    JITTER: Literal['jitter'] = 'jitter'
    FIBONACCI: Literal['fibonacci'] = 'fibonacci'
    RANDOM: Literal['random'] = 'random'
