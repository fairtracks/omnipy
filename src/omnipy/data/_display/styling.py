from enum import Enum
from functools import cached_property
from io import StringIO
from typing import Generic, overload

from rich.console import Console, OverflowMethod
from rich.syntax import Syntax

from omnipy.data._display.config import (HorizontalOverflowMode,
                                         MAX_TERMINAL_SIZE,
                                         VerticalOverflowMode)
from omnipy.data._display.draft import DraftMonospacedOutput, FrameT
from omnipy.util._pydantic import ConfigDict, dataclass, Extra


class OutputMode(str, Enum):
    PLAIN = 'plain'
    BW_STYLIZED = 'bw_stylized'
    COLORIZED = 'colorized'


class OutputVariant:
    def __init__(self,
                 console: Console,
                 output_mode: OutputMode,
                 frame_height: int | None,
                 vertical_overflow_mode: VerticalOverflowMode) -> None:
        self._console = console
        self._output_mode = output_mode
        self._frame_height = frame_height
        self._vertical_overflow_mode = vertical_overflow_mode

    def _vertical_crop(self, text: str) -> str:
        if self._frame_height is None:
            return text

        lines = text.splitlines(keepends=True)
        if len(lines) <= self._frame_height:
            return text

        match (self._vertical_overflow_mode):
            case VerticalOverflowMode.CROP_BOTTOM:
                return ''.join(lines[:self._frame_height])
            case VerticalOverflowMode.CROP_TOP:
                return ''.join(lines[-self._frame_height:])

    @cached_property
    def terminal(self) -> str:
        if self._output_mode is OutputMode.PLAIN:
            text = self._console.export_text(clear=False, styles=False)
        else:
            text = self._console.end_capture()
        return self._vertical_crop(text)


@dataclass(config=ConfigDict(extra=Extra.forbid, validate_all=True))
class StylizedMonospacedOutput(DraftMonospacedOutput[FrameT], Generic[FrameT]):
    @overload
    def __init__(self, content: DraftMonospacedOutput[FrameT]):
        ...

    @overload
    def __init__(self, content: str, frame=None, constraints=None, config=None):
        ...

    def __init__(self,
                 content: str | DraftMonospacedOutput[FrameT],
                 frame=None,
                 constraints=None,
                 config=None):
        if isinstance(content, DraftMonospacedOutput):
            assert frame is None
            assert constraints is None
            assert config is None

            str_content = content.content
            frame = content.frame
            constraints = content.constraints
            config = content.config
        else:
            str_content = content

        super().__init__(str_content, frame, constraints, config)

    @cached_property
    def _stylized_content(self) -> Syntax:
        color_style = self.config.color_style
        style_name = color_style.value if isinstance(color_style, Enum) else 'default'
        word_wrap = self.config.horizontal_overflow_mode == HorizontalOverflowMode.WORD_WRAP

        return Syntax(
            self.content,
            'python',
            theme=style_name,
            background_color='default',
            word_wrap=word_wrap,
        )

    def _get_console_frame_width_and_height(self) -> tuple[int, int]:
        frame_width = self.frame.dims.width
        frame_height = self.frame.dims.height

        return (
            frame_width if frame_width is not None else MAX_TERMINAL_SIZE,
            frame_height if frame_height is not None else MAX_TERMINAL_SIZE,
        )

    def _get_console_overload(self) -> OverflowMethod | None:
        match (self.config.horizontal_overflow_mode):
            case HorizontalOverflowMode.ELLIPSIS:
                return 'ellipsis'
            case HorizontalOverflowMode.CROP:
                return 'crop'
            case HorizontalOverflowMode.WORD_WRAP:
                return None

    def _console(self, output_mode: OutputMode) -> Console:
        width, height = self._get_console_frame_width_and_height()

        console = Console(
            file=StringIO(),
            width=width,
            height=height,
            color_system='truecolor' if output_mode == OutputMode.COLORIZED else 'standard',
            no_color=False if output_mode == OutputMode.COLORIZED else True,
            record=True,
        )

        overflow = self._get_console_overload()
        soft_wrap = True if self.frame.dims.width is None else False
        if output_mode is OutputMode.BW_STYLIZED:
            console.begin_capture()
        console.print(self._stylized_content, overflow=overflow, soft_wrap=soft_wrap)

        return console

    @cached_property
    def plain(self) -> OutputVariant:
        return OutputVariant(
            self._console(OutputMode.PLAIN),
            OutputMode.PLAIN,
            self.frame.dims.height,
            self.config.vertical_overflow_mode,
        )

    @cached_property
    def bw_stylized(self) -> OutputVariant:
        return OutputVariant(
            self._console(OutputMode.BW_STYLIZED),
            OutputMode.BW_STYLIZED,
            self.frame.dims.height,
            self.config.vertical_overflow_mode,
        )

    @cached_property
    def _content_lines(self) -> list[str]:
        return self.plain.terminal.splitlines()
