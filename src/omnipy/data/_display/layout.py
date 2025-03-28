from collections import UserDict
from typing import Callable, Iterator, Mapping

from typing_extensions import TypeIs, TypeVar

from omnipy.data._display.dimensions import DimensionsWithWidthAndHeight
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FullyRenderedPanel,
                                             panel_is_dimensions_aware,
                                             panel_is_fully_rendered)
from omnipy.data._display.panel.draft import Panel

PanelT = TypeVar('PanelT', bound=Panel)


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

    def _render_until_criteria_holds(
            self, criteria: Callable[[Panel], TypeIs[PanelT]]) -> Mapping[str, PanelT]:
        finished_panels: dict[str, PanelT] = {}
        remaining_panels: dict[str, Panel] = self.data.copy()

        while len(remaining_panels) > 0:
            newly_rendered_panels = {}
            for key, panel in remaining_panels.items():
                if criteria(panel):
                    finished_panels[key] = panel
                else:
                    newly_rendered_panels[key] = panel.render_next_stage()

            remaining_panels = newly_rendered_panels

        return finished_panels

    def render_until_dimensions_aware(self) -> Mapping[str, DimensionsAwarePanel[AnyFrame]]:
        """Render all panels in the layout until they have calculated their dimensions."""
        return self._render_until_criteria_holds(panel_is_dimensions_aware)

    def render_fully(self) -> Mapping[str, FullyRenderedPanel[AnyFrame]]:
        """Render all panels in the layout until they are fully rendered."""
        return self._render_until_criteria_holds(panel_is_fully_rendered)
