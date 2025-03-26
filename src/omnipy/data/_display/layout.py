from collections import UserDict
from typing import Iterator

from omnipy.data._display.dimensions import DimensionsWithWidthAndHeight
from omnipy.data._display.panel.draft import Panel


class Grid:
    """Class to represent a grid of panels with coordinate-based access."""
    def __init__(self, layout: 'Layout'):
        self._layout = layout

    @property
    def dims(self) -> DimensionsWithWidthAndHeight:
        """Return the dimensions of the grid (width, height)."""
        return DimensionsWithWidthAndHeight(
            width=len(self._layout), height=1 if len(self._layout) > 0 else 0)

    def __getitem__(self, key: tuple[int, int]) -> str:
        """Get panel from the grid at specific coordinates."""
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError('Grid coordinates must be a tuple of (x, y)')

        x, y = key

        # Check if coordinates are valid
        if x != 0 or y < 0 or y >= len(self._layout):
            raise IndexError('Grid index out of range')

        # Get the item at the specified position (in insertion order)
        keys = list(self._layout.keys())
        return keys[y]


class Layout(UserDict[str, Panel]):
    """A class representing a layout of panels.

    This class inherits from `UserDict` to provide a dictionary-like
    interface for managing panels in a layout. It allows adding, removing,
    and accessing panels by their names, and other dictionary operations.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grid = Grid(self)

    def __reversed__(self) -> Iterator[str]:
        """Return keys in the reversed order"""
        return reversed(self.data.keys())

    @property
    def grid(self) -> Grid:
        """Return a Grid object for coordinate-based access."""
        return self._grid

    def __hash__(self) -> int:
        return hash((tuple(self.data.keys()), tuple(self.data.values())))
