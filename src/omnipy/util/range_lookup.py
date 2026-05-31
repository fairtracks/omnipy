"""Fast membership lookup for collections of non-negative integer ranges.

This module compacts a set of ``range`` objects into a bitarray-backed lookup
table for repeated containment checks.
"""

from collections.abc import Iterable

from bitarray import bitarray


class RangeLookup:
    """Provide constant-time containment checks for integer ranges.

    Args:
        ranges: Ranges to encode into the lookup table.

    Raises:
        ValueError: If any range contains negative values.
    """
    def __init__(self, ranges: Iterable[range]):
        largest_range_stop = max((r.stop for r in ranges), default=0)
        if largest_range_stop >= 0:
            self._range_array = bitarray(largest_range_stop)
        for range_ in ranges:
            if range_.start < 0 or range_.stop < 0:
                raise ValueError(f'Negative numbers are not supported for ranges: {range_}')
            self._range_array[range_] = 1

    def __contains__(self, number: int) -> bool:
        if number < 0:
            raise ValueError(f'Negative numbers are not supported for lookup: {number}')
        if number >= len(self._range_array):
            return False
        return bool(self._range_array[number])
