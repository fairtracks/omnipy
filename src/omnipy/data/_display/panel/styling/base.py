from abc import ABC, abstractmethod
from functools import cached_property, lru_cache
from io import StringIO
from typing import Generic, TypeAlias

import rich.console
import rich.panel
import rich.style
import rich.syntax
import rich.table
from typing_extensions import override, TypeVar

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.panel.base import FullyRenderedPanel, OutputVariant
from omnipy.data._display.panel.cropping import rich_overflow_method
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.data._display.panel.typedefs import ContentT, FrameT
from omnipy.shared.enums.display import DisplayColorSystem
from omnipy.shared.enums.ui import SpecifiedUserInterfaceType, UserInterfaceType
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
    # TODO: Return to _inner_cropped_dims when Pydantic 2.0 is released
    #
    # Pydantic 1.10 emits a RuntimeWarning for dataclasses with private
    # fields (starting with '_')
    # See https://github.com/pydantic/pydantic/issues/2816
    # _inner_cropped_dims: DimensionsWithWidthAndHeight = Dimensions(width=0, height=0)

    inner_cropped_dims: DimensionsWithWidthAndHeight = Dimensions(width=0, height=0)

    def __init__(self, panel: MonospacedDraftPanel[ContentT, FrameT]):
        super().__init__(
            panel.content,
            title=panel.title,
            frame=panel.frame,
            constraints=panel.constraints,
            config=panel.config,
        )
        # object.__setattr__(self, '_inner_cropped_dims', panel.cropped_dims)
        object.__setattr__(self, 'inner_cropped_dims', self._calc_inner_cropped_dims(panel))

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

    @staticmethod
    def _calc_inner_cropped_dims(
            panel: MonospacedDraftPanel[ContentT, FrameT]) -> DimensionsWithWidthAndHeight:
        return panel.inner_frame.crop_dims(panel.dims, ignore_fixed_dims=True)

    @cached_property
    def _console_dimensions(self) -> DimensionsWithWidthAndHeight:
        return self._apply_console_newline_hack(self.inner_cropped_dims)

    @staticmethod
    def _apply_console_newline_hack(
            console_dims: DimensionsWithWidthAndHeight) -> DimensionsWithWidthAndHeight:
        """
        Hack to allow rich.console to output newline content when
        width == 0
        """
        if console_dims.width == 0 and console_dims.height > 0:
            return Dimensions(width=1, height=console_dims.height)

        return console_dims

    @cached_property
    def rich_overflow_method(self) -> rich.console.OverflowMethod | None:
        return rich_overflow_method(self.config.h_overflow)

    @staticmethod
    @lru_cache(maxsize=1024)
    def _get_console_common(
        stylized_content: rich.console.RenderableType,
        console_width: int,
        console_height: int,
        frame_width: int | None,
        rich_overflow_method: rich.console.OverflowMethod | None,
        color_system: DisplayColorSystem.Literals,
        ui_type: SpecifiedUserInterfaceType.Literals,
    ) -> rich.console.Console:

        console = rich.console.Console(
            file=StringIO(),
            width=console_width,
            height=console_height,
            color_system=color_system,
            record=True,
            force_jupyter=False,
            force_terminal=UserInterfaceType.is_terminal(ui_type),
        )

        soft_wrap = True if frame_width is None else False
        console.print(stylized_content, overflow=rich_overflow_method, soft_wrap=soft_wrap)

        return console

    @property
    def _console_terminal(self) -> rich.console.Console:
        return self._get_console_common(
            stylized_content=self._stylized_content_terminal,
            console_width=self._console_dimensions.width,
            console_height=self._console_dimensions.height,
            frame_width=self.frame.dims.width,
            rich_overflow_method=self.rich_overflow_method,
            ui_type=self.config.ui,
            color_system=self.config.system,
        )

    @property
    def _console_html(self) -> rich.console.Console:
        # Color system is hard-coded to 'truecolor' for HTML output
        return self._get_console_common(
            stylized_content=self._stylized_content_html,
            console_width=self._console_dimensions.width,
            console_height=self._console_dimensions.height,
            frame_width=self.frame.dims.width,
            rich_overflow_method=self.rich_overflow_method,
            ui_type=self.config.ui,
            color_system=DisplayColorSystem.ANSI_RGB,
        )

    @cached_property
    @override
    def _content_lines(self) -> list[str]:
        """
        Returns the plain terminal output of the panel as a list of lines.
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
