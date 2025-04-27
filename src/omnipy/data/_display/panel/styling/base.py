from abc import ABC, abstractmethod
from functools import cache, cached_property
from io import StringIO
from typing import Generic, TypeAlias

import rich.box
import rich.color
import rich.color_triplet
import rich.console
import rich.panel
import rich.segment
import rich.style
import rich.syntax
import rich.table
import rich.terminal_theme
import rich.text
from typing_extensions import override, TypeVar

from omnipy.data._display.config import ConsoleColorSystem, HorizontalOverflowMode
from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width)
from omnipy.data._display.panel.base import FullyRenderedPanel, OutputVariant
from omnipy.data._display.panel.draft.base import ContentT, FrameT
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
import omnipy.util._pydantic as pyd

StylizedRichTypes: TypeAlias = rich.syntax.Syntax | rich.panel.Panel | rich.table.Table

PanelT = TypeVar('PanelT', bound=MonospacedDraftPanel, covariant=True)


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True, arbitrary_types_allowed=True),
)
class StylizedMonospacedPanel(
        FullyRenderedPanel[FrameT],
        MonospacedDraftPanel[ContentT, FrameT],
        Generic[PanelT, ContentT, FrameT],
        ABC,
):
    # TODO: Return to _panel_calculated_dims when Pydantic 2.0 is released
    #
    # Pydantic 1.10 emits a RuntimeWarning for dataclasses with private
    # fields (starting with '_')
    # See https://github.com/pydantic/pydantic/issues/2816
    # _panel_calculated_dims: DimensionsWithWidthAndHeight = Dimensions(width=0, height=0)

    panel_calculated_dims: DimensionsWithWidthAndHeight = Dimensions(width=0, height=0)

    def __init__(self, panel: MonospacedDraftPanel[ContentT, FrameT]):
        super().__init__(panel.content, panel.frame, panel.constraints, panel.config)
        # object.__setattr__(self, '_panel_calculated_dims', panel.dims)
        object.__setattr__(self, 'panel_calculated_dims', panel.dims)

    @staticmethod
    def _clean_rich_style_caches():
        """
        Clears object-level caches of the Style class in the Rich library to ensure that the current
        color system is used to render the output. This is needed as the Style caches do not take
        the current color system into account.

        """

        # The cache of the '_add()' method is the main cache causing issues
        rich.style.Style._add.cache_clear()

        # However, we clean these caches as well to be sure
        rich.style.Style.get_html_style.cache_clear()
        rich.style.Style.clear_meta_and_links.cache_clear()

    @cached_property
    def _stylized_content_terminal(self) -> StylizedRichTypes:
        self._clean_rich_style_caches()
        return self._stylized_content_terminal_impl()

    @cached_property
    def _stylized_content_html(self) -> StylizedRichTypes:
        self._clean_rich_style_caches()
        return self._stylized_content_html_impl()

    @abstractmethod
    def _stylized_content_terminal_impl(self) -> StylizedRichTypes:
        """
        Returns the stylized content for the terminal output. This is a
        placeholder method to be overridden by subclasses.
        """

    @abstractmethod
    def _stylized_content_html_impl(self) -> StylizedRichTypes:
        """
        Returns the stylized content for the HTML output. This is a
        placeholder method to be overridden by subclasses.
        """

    @cached_property
    def _console_dimensions(self) -> DimensionsWithWidthAndHeight:
        frame_dims = self.frame.dims
        panel_dims = self.panel_calculated_dims

        console_width = frame_dims.width if has_width(frame_dims) else panel_dims.width
        console_height = frame_dims.height if has_height(frame_dims) else panel_dims.height

        return self._apply_console_newline_hack(
            Dimensions(width=console_width, height=console_height))

    def _apply_console_newline_hack(
            self, console_dims: DimensionsWithWidthAndHeight) -> DimensionsWithWidthAndHeight:
        """
        Hack to allow rich.console to output newline contents when
        width == 0
        """
        panel_dims = self.panel_calculated_dims
        if panel_dims.width == 0 and console_dims.width == 0 and console_dims.height > 0:
            return Dimensions(width=1, height=console_dims.height)

        return console_dims

    @staticmethod
    @cache
    def _get_console_common(
        stylized_content: rich.console.RenderableType,
        console_width: int,
        console_height: int,
        frame_width: int | None,
        console_color_system: ConsoleColorSystem,
        horizontal_overflow_mode: HorizontalOverflowMode,
    ) -> rich.console.Console:
        def _map_horizontal_overflow_mode_to_console_overflow_method(
                horizontal_overflow_mode: HorizontalOverflowMode
        ) -> rich.console.OverflowMethod | None:
            match (horizontal_overflow_mode):
                case HorizontalOverflowMode.ELLIPSIS:
                    return 'ellipsis'
                case HorizontalOverflowMode.CROP:
                    return 'crop'
                case HorizontalOverflowMode.WORD_WRAP:
                    return None

        console = rich.console.Console(
            file=StringIO(),
            width=console_width,
            height=console_height,
            color_system=console_color_system.value,
            record=True,
        )

        overflow_method = _map_horizontal_overflow_mode_to_console_overflow_method(
            horizontal_overflow_mode)
        soft_wrap = True if frame_width is None else False
        console.print(stylized_content, overflow=overflow_method, soft_wrap=soft_wrap)

        return console

    @property
    def _console_terminal(self) -> rich.console.Console:
        return self._get_console_common(
            stylized_content=self._stylized_content_terminal,
            console_width=self._console_dimensions.width,
            console_height=self._console_dimensions.height,
            frame_width=self.frame.dims.width,
            console_color_system=self.config.console_color_system,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
        )

    @property
    def _console_html(self) -> rich.console.Console:
        # Color system is hard-coded to 'truecolor' for HTML output
        return self._get_console_common(
            stylized_content=self._stylized_content_html,
            console_width=self._console_dimensions.width,
            console_height=self._console_dimensions.height,
            frame_width=self.frame.dims.width,
            console_color_system=ConsoleColorSystem.ANSI_RGB,
            horizontal_overflow_mode=self.config.horizontal_overflow_mode,
        )

    @cached_property
    @override
    def _content_lines(self) -> list[str]:
        """
        Returns the plain terminal output of the panel as a list of lines.
        Here, as compared to output should end with a
        """
        return self.plain.terminal.splitlines()

    @cached_property
    @abstractmethod
    def plain(self) -> OutputVariant:
        ...

    @cached_property
    @abstractmethod
    def bw_stylized(self) -> OutputVariant:
        ...

    @cached_property
    @abstractmethod
    def colorized(self) -> OutputVariant:
        ...
