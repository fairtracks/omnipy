"""Core layout objects that compose panels into a single-row arrangement."""

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
    """Single-row grid view over a :class:`Layout`.

    The grid provides coordinate-style access for layout rendering code while
    preserving insertion order from the underlying mapping.
    """
    def __init__(self, layout: 'Layout[PanelT]'):
        """Initialize a single-row grid wrapper for a panel layout."""
        self._layout = layout

    @property
    def dims(self) -> DimensionsWithWidthAndHeight:
        """Return dimensions of the grid coordinate space.

        Returns:
            Width equals number of panels in the row and height is ``1`` when
            panels exist, otherwise ``0``.
        """
        return DimensionsWithWidthAndHeight(
            width=len(self._layout), height=1 if len(self._layout) > 0 else 0)

    def __getitem__(self, key: tuple[int, int]) -> str:
        """Return the panel key located at the given ``(x, y)`` coordinates."""
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
        """Yield all panels in the requested row.

        Args:
            row_index: Row index in the single-row grid.

        Returns:
            Iterable over panels in insertion order for the row.
        """
        return (self._layout[self[(row_index, i)]] for i in range(self.dims.width))


class Layout(UserDict[str, PanelT], Generic[PanelT]):
    """Ordered mapping from panel keys to panel objects."""
    def __init__(self, *args, **kwargs):
        """Initialize layout storage and its coordinate-style grid accessor."""
        super().__init__(*args, **kwargs)
        self._grid = Grid(self)

    def __reversed__(self) -> Iterator[str]:
        """Return keys in the reversed order"""
        return reversed(self.data.keys())

    @property
    def grid(self) -> Grid:
        """Return the coordinate-based grid accessor for this layout.

        Returns:
            ``Grid`` wrapper exposing row/column style access.
        """
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
        """Render each panel until it reaches dimensions-aware stage.

        Returns:
            Mapping from panel key to dimensions-aware panel in original order.
        """
        return self._render_until_criteria_holds(panel_is_dimensions_aware)

    def render_fully(self) -> Mapping[str, FullyRenderedPanel]:
        """Render each panel until it reaches fully rendered stage.

        Returns:
            Mapping from panel key to fully rendered panel in original order.
        """
        return self._render_until_criteria_holds(panel_is_fully_rendered)


@dataclass
class PanelDesignDims:
    """Border and spacing overhead associated with a panel design.

    Instances capture per-panel and terminal-edge overhead used when converting
    content dimensions to full rendered table dimensions.
    """

    num_horizontal_chars_per_panel: int
    num_horizontal_end_chars: int
    num_vertical_lines_per_panel: int
    num_vertical_end_lines: int

    @staticmethod
    def _extra_chars(chars_per_panel: int, end_chars: int, num_panels: int) -> int:
        return num_panels * chars_per_panel + end_chars

    def num_extra_horizontal_chars(self, num_horizontal_panels: int) -> int:
        """Return horizontal border/separator overhead for a panel row.

        Args:
            num_horizontal_panels: Number of panels rendered horizontally.

        Returns:
            Number of non-content characters added by the panel design.
        """
        return self._extra_chars(
            self.num_horizontal_chars_per_panel,
            self.num_horizontal_end_chars,
            num_horizontal_panels,
        )

    def num_extra_vertical_chars(self, num_vertical_panels: int) -> int:
        """Return vertical border/separator overhead for panel rows.

        Args:
            num_vertical_panels: Number of panel rows.

        Returns:
            Number of non-content lines added by the panel design.
        """
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
        """Return how many panels fit within a frame width.

        Args:
            frame_width: Available frame width in characters.
            width_per_panel: Content width allocated per panel.

        Returns:
            Maximum number of full panels that fit horizontally.
        """
        return self._num_panels_within_frame_dim(
            self.num_horizontal_chars_per_panel,
            self.num_horizontal_end_chars,
            frame_width,
            width_per_panel,
        )

    def num_panels_within_frame_height(self, frame_height: int, height_per_panel: int) -> int:
        """Return how many panel rows fit within a frame height.

        Args:
            frame_height: Available frame height in lines.
            height_per_panel: Content height allocated per panel row.

        Returns:
            Maximum number of full panel rows that fit vertically.
        """
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
        """Build design-overhead values for a specific panel style.

        Args:
            panel_design: Panel design enum to translate into overhead values.

        Returns:
            ``PanelDesignDims`` configured for the requested design.

        Raises:
            ValueError: If the panel design is unsupported.
        """
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
    """Layout mixin that derives aggregate dimensions from rendered subpanels."""
    def _total_dims_over_subpanels(self, dims_property: str) -> DimensionsWithWidthAndHeight:
        self_as_layout = cast(Layout, self)

        all_panel_dims = [getattr(panel, dims_property) for panel in self_as_layout.values()]
        return Dimensions(
            width=sum(panel_dims.width for panel_dims in all_panel_dims),
            height=max((panel_dims.height for panel_dims in all_panel_dims), default=0))

    @property
    def total_subpanel_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        """Return combined cropped dimensions of all subpanels.

        Returns:
            Width as sum of cropped widths and height as maximum cropped height.
        """
        return self._total_dims_over_subpanels('cropped_dims')

    @property
    def total_subpanel_outer_dims(self) -> DimensionsWithWidthAndHeight:
        """Return combined outer dimensions of all subpanels.

        Returns:
            Width as sum of outer widths and height as maximum outer height.
        """
        return self._total_dims_over_subpanels('outer_dims')

    def calc_dims(
        self,
        panel_design: PanelDesign.Literals = PanelDesign.TABLE,
        use_outer_dims_for_subpanels: bool = True,
    ) -> DimensionsWithWidthAndHeight:
        """Calculate overall layout dimensions including panel design overhead.

        Args:
            panel_design: Table/panel design used to compute border overhead.
            use_outer_dims_for_subpanels: Whether subpanel dimensions should
                include title/border-aware outer sizes.

        Returns:
            Calculated dimensions for the composed layout.
        """
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
