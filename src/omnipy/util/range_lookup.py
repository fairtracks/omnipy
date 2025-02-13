from collections.abc import Iterable

from bitarray import bitarray


class RangeLookup:
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
