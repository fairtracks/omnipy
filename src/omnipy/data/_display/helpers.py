from rich._cell_widths import CELL_WIDTHS

from omnipy.util.range_lookup import RangeLookup


class UnicodeCharWidthMap:
    def __init__(self) -> None:
        width_0_ranges = []
        width_2_ranges = []

        for start, stop_inclusive, width in CELL_WIDTHS:
            cur_range = range(start, stop_inclusive + 1)
            if width <= 0:
                width_0_ranges.append(cur_range)
            elif width == 2:
                width_2_ranges.append(cur_range)

        self._chars_with_width_0 = RangeLookup(width_0_ranges)
        self._chars_with_width_2 = RangeLookup(width_2_ranges)

    def __getitem__(self, char: str) -> int:
        unicode_index = ord(char)
        if unicode_index in self._chars_with_width_0:
            return 0
        if unicode_index in self._chars_with_width_2:
            return 2
        return 1
