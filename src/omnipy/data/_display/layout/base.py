from collections import UserDict
from dataclasses import dataclass
from typing import Callable, cast, Generic, Iterable, Iterator, Mapping

from typing_extensions import TypeIs, TypeVar

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.panel.base import (DimensionsAwarePanel,
                                             FullyRenderedPanel,
                                             Panel,
                                             panel_is_dimensions_aware,
                                             panel_is_fully_rendered)
from omnipy.shared.enums.display import PanelDesign

PanelT = TypeVar('PanelT', bound=Panel)
RenderedPanelT = TypeVar('RenderedPanelT', bound=Panel)


class Grid(Generic[PanelT]):
    """Class to represent a grid of panels with coordinate-based access."""
    def __init__(self, layout: 'Layout[PanelT]'):
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

    def get_row(self, row_index: int) -> Iterable[PanelT]:
        return (self._layout[self[(row_index, i)]] for i in range(self.dims.width))


class Layout(UserDict[str, PanelT], Generic[PanelT]):
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
            self, criteria: Callable[[Panel], TypeIs[RenderedPanelT]]) -> dict[str, RenderedPanelT]:
        finished_panels: dict[str, RenderedPanelT] = {}
        remaining_panels: dict[str, Panel] = self.data.copy()  # type: ignore[assignment]

        while len(remaining_panels) > 0:
            newly_rendered_panels: dict[str, Panel] = {}
            for key, panel in remaining_panels.items():
                if criteria(panel):
                    finished_panels[key] = panel
                else:
                    newly_rendered_panels[key] = panel.render_next_stage()

            remaining_panels = newly_rendered_panels

        return {key: finished_panels[key] for key in self.data.keys()}

    def render_until_dimensions_aware(self) -> dict[str, DimensionsAwarePanel]:
        """Render all panels in the layout until they have calculated their dimensions."""
        return self._render_until_criteria_holds(panel_is_dimensions_aware)

    def render_fully(self) -> Mapping[str, FullyRenderedPanel]:
        """Render all panels in the layout until they are fully rendered."""
        return self._render_until_criteria_holds(panel_is_fully_rendered)


@dataclass
class PanelDesignDims:
    num_horizontal_chars_per_panel: int
    num_horizontal_end_chars: int
    num_vertical_lines_per_panel: int
    num_vertical_end_lines: int

    @staticmethod
    def _extra_chars(chars_per_panel: int, end_chars: int, num_panels: int) -> int:
        return num_panels * chars_per_panel + end_chars

    def num_extra_horizontal_chars(self, num_horizontal_panels: int) -> int:
        return self._extra_chars(
            self.num_horizontal_chars_per_panel,
            self.num_horizontal_end_chars,
            num_horizontal_panels,
        )

    def num_extra_vertical_chars(self, num_vertical_panels: int) -> int:
        return self._extra_chars(
            self.num_vertical_lines_per_panel,
            self.num_vertical_end_lines,
            num_vertical_panels,
        )

    @staticmethod
    def _num_panels_within_frame_dim(
        chars_per_panel: int,
        end_chars: int,
        frame_dim_val: int,
        content_dim_val_per_panel: int,
    ) -> int:
        available_dim_val = frame_dim_val - end_chars
        dim_val_per_panel = chars_per_panel + content_dim_val_per_panel
        return available_dim_val // dim_val_per_panel

    def num_panels_within_frame_width(self, frame_width: int, width_per_panel: int) -> int:
        return self._num_panels_within_frame_dim(
            self.num_horizontal_chars_per_panel,
            self.num_horizontal_end_chars,
            frame_width,
            width_per_panel,
        )

    def num_panels_within_frame_height(self, frame_height: int, height_per_panel: int) -> int:
        return self._num_panels_within_frame_dim(
            self.num_vertical_lines_per_panel,
            self.num_vertical_end_lines,
            frame_height,
            height_per_panel,
        )

    @classmethod
    def create(
        cls,
        panel_design: PanelDesign.Literals = PanelDesign.TABLE,
    ) -> 'PanelDesignDims':
        match panel_design:
            case PanelDesign.TABLE:
                return PanelDesignDims(
                    num_horizontal_chars_per_panel=3,
                    num_horizontal_end_chars=1,
                    num_vertical_lines_per_panel=1,
                    num_vertical_end_lines=1,
                )
            case PanelDesign.TABLE_SHOW_STYLE:
                return PanelDesignDims(
                    num_horizontal_chars_per_panel=3,
                    num_horizontal_end_chars=1,
                    num_vertical_lines_per_panel=1,
                    num_vertical_end_lines=2,
                )
            case _:
                raise ValueError(f'Unsupported panel design: {panel_design}')


class DimensionsAwarePanelLayoutMixin:
    def _total_dims_over_subpanels(self, dims_property: str) -> DimensionsWithWidthAndHeight:
        self_as_layout = cast(Layout, self)

        all_panel_dims = [getattr(panel, dims_property) for panel in self_as_layout.values()]
        return Dimensions(
            width=sum(panel_dims.width for panel_dims in all_panel_dims),
            height=max((panel_dims.height for panel_dims in all_panel_dims), default=0))

    @property
    def total_subpanel_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        return self._total_dims_over_subpanels('cropped_dims')

    @property
    def total_subpanel_outer_dims(self) -> DimensionsWithWidthAndHeight:
        return self._total_dims_over_subpanels('outer_dims')

    def calc_dims(
        self,
        panel_design: PanelDesign.Literals = PanelDesign.TABLE,
        use_outer_dims_for_subpanels: bool = True,
    ) -> DimensionsWithWidthAndHeight:
        self_as_layout = cast(Layout, self)

        if len(self_as_layout) > 0:
            if use_outer_dims_for_subpanels:
                total_subpanel_dims = self.total_subpanel_outer_dims
            else:
                total_subpanel_dims = self.total_subpanel_cropped_dims

            panel_design_dims = PanelDesignDims.create(panel_design)

            num_horizontal_panels = len(self_as_layout)
            num_vertical_panels = 1  # Assuming a single row layout for simplicity
            return Dimensions(
                width=(total_subpanel_dims.width
                       + panel_design_dims.num_extra_horizontal_chars(num_horizontal_panels)),
                height=(total_subpanel_dims.height
                        + panel_design_dims.num_extra_vertical_chars(num_vertical_panels)),
            )
        else:
            return Dimensions(width=0, height=1)
