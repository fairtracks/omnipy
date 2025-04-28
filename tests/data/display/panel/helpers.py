from dataclasses import dataclass, field
import re
from typing import Callable, Generic, TypeAlias, TypedDict

import pytest
from typing_extensions import NamedTuple, TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width)
from omnipy.data._display.frame import empty_frame, Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT, Panel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd

OutputPropertyType: TypeAlias = Callable[[SyntaxStylizedTextPanel | StylizedLayoutPanel], str]
ContentT = TypeVar('ContentT', bound=str | Layout)

# Classes


class DraftPanelKwArgs(TypedDict, total=False):
    frame: Frame
    constraints: Constraints
    config: OutputConfig


class FrameVariant(NamedTuple):
    use_frame_width: bool
    use_frame_height: bool


class WithinFrameExp(NamedTuple):
    width: bool | None
    height: bool | None
    both: bool | None


@dataclass
class FrameTestCase(Generic[FrameT]):
    frame: FrameT | None
    config: OutputConfig | None = None

    exp_plain_output: str | None | pyd.UndefinedType = field(default=pyd.Undefined)
    exp_dims_all_stages: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_resized_dims: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_stylized_dims: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)

    exp_plain_output_only_width: str | None | pyd.UndefinedType = field(default=pyd.Undefined)
    exp_dims_all_stages_only_width: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_resized_dims_only_width: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_stylized_dims_only_width: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)

    exp_plain_output_only_height: str | None | pyd.UndefinedType = field(default=pyd.Undefined)
    exp_dims_all_stages_only_height: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_resized_dims_only_height: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_stylized_dims_only_height: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)

    def __post_init__(self):
        assert not (self.exp_dims_all_stages is not pyd.Undefined
                    and self.exp_resized_dims is not pyd.Undefined)
        assert not (self.exp_dims_all_stages is not pyd.Undefined
                    and self.exp_stylized_dims is not pyd.Undefined)
        assert not (self.exp_dims_all_stages_only_width is not pyd.Undefined
                    and self.exp_resized_dims_only_width is not pyd.Undefined)
        assert not (self.exp_dims_all_stages_only_width is not pyd.Undefined
                    and self.exp_stylized_dims_only_width is not pyd.Undefined)
        assert not (self.exp_dims_all_stages_only_height is not pyd.Undefined
                    and self.exp_resized_dims_only_height is not pyd.Undefined)
        assert not (self.exp_dims_all_stages_only_height is not pyd.Undefined
                    and self.exp_stylized_dims_only_height is not pyd.Undefined)


@dataclass
class PanelFrameVariantTestCase(Generic[ContentT, FrameT]):
    content: ContentT
    frame: FrameWithWidthAndHeight | None
    config: OutputConfig | None
    exp_plain_output_no_frame: str | None
    exp_dims_all_stages_no_frame: DimensionsWithWidthAndHeight
    frame_case: FrameTestCase[FrameT]
    frame_variant: FrameVariant

    exp_plain_output: str | None | pyd.UndefinedType = field(default=pyd.Undefined)
    exp_dims_all_stages: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_resized_dims: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_stylized_dims: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)

    exp_plain_output_only_width: str | None | pyd.UndefinedType = field(default=pyd.Undefined)
    exp_dims_all_stages_only_width: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_resized_dims_only_width: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_stylized_dims_only_width: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)

    exp_plain_output_only_height: str | None | pyd.UndefinedType = field(default=pyd.Undefined)
    exp_dims_all_stages_only_height: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_resized_dims_only_height: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)
    exp_stylized_dims_only_height: DimensionsWithWidthAndHeight | pyd.UndefinedType = field(
        default=pyd.Undefined)

    def __post_init__(self):
        def _resolve_to_first_defined(*values):
            """Helper to resolve the first non-Undefined value."""
            for value in values:
                if value is not pyd.Undefined:
                    return value
            return pyd.Undefined

        # General fields
        self.exp_plain_output = _resolve_to_first_defined(
            self.frame_case.exp_plain_output,
            self.exp_plain_output,
            self.exp_plain_output_no_frame,
        )
        self.exp_dims_all_stages = _resolve_to_first_defined(
            self.frame_case.exp_dims_all_stages,
            self.exp_dims_all_stages,
        )
        self.exp_resized_dims = _resolve_to_first_defined(
            self.frame_case.exp_resized_dims,
            self.exp_resized_dims,
            self.exp_dims_all_stages,
            self.exp_dims_all_stages_no_frame,
        )
        self.exp_stylized_dims = _resolve_to_first_defined(
            self.frame_case.exp_stylized_dims,
            self.exp_stylized_dims,
            self.exp_dims_all_stages,
            self.exp_dims_all_stages_no_frame,
        )

        assert not isinstance(self.exp_resized_dims, pyd.UndefinedType)
        assert not isinstance(self.exp_stylized_dims, pyd.UndefinedType)

        # "Only width" fields
        self.exp_plain_output_only_width = _resolve_to_first_defined(
            self.frame_case.exp_plain_output_only_width,
            self.exp_plain_output_only_width,
            self.exp_plain_output,
            self.exp_plain_output_no_frame,
        )
        self.exp_dims_all_stages_only_width = _resolve_to_first_defined(
            self.frame_case.exp_dims_all_stages_only_width,
            self.exp_dims_all_stages_only_width,
            self.exp_dims_all_stages,
        )
        self.exp_resized_dims_only_width = _resolve_to_first_defined(
            self.frame_case.exp_resized_dims_only_width,
            self.exp_resized_dims_only_width,
            self.exp_dims_all_stages_only_width,
            self.frame_case.exp_resized_dims,
            Dimensions(
                width=self.exp_resized_dims.width,
                height=self.exp_dims_all_stages_no_frame.height,
            ),
        )
        self.exp_stylized_dims_only_width = _resolve_to_first_defined(
            self.frame_case.exp_stylized_dims_only_width,
            self.exp_stylized_dims_only_width,
            self.exp_dims_all_stages_only_width,
            self.frame_case.exp_stylized_dims,
            Dimensions(
                width=self.exp_stylized_dims.width,
                height=self.exp_dims_all_stages_no_frame.height,
            ),
        )

        # "Only height" fields
        self.exp_plain_output_only_height = _resolve_to_first_defined(
            self.frame_case.exp_plain_output_only_height,
            self.exp_plain_output_only_height,
            self.exp_plain_output,
            self.exp_plain_output_no_frame,
        )
        self.exp_dims_all_stages_only_height = _resolve_to_first_defined(
            self.frame_case.exp_dims_all_stages_only_height,
            self.exp_dims_all_stages_only_height,
            self.exp_dims_all_stages,
        )
        self.exp_resized_dims_only_height = _resolve_to_first_defined(
            self.frame_case.exp_resized_dims_only_height,
            self.exp_resized_dims_only_height,
            self.exp_dims_all_stages_only_height,
            self.frame_case.exp_resized_dims,
            Dimensions(
                width=self.exp_dims_all_stages_no_frame.width,
                height=self.exp_resized_dims.height,
            ),
        )
        self.exp_stylized_dims_only_height = _resolve_to_first_defined(
            self.frame_case.exp_stylized_dims_only_height,
            self.exp_stylized_dims_only_height,
            self.exp_dims_all_stages_only_height,
            self.frame_case.exp_stylized_dims,
            Dimensions(
                width=self.exp_dims_all_stages_no_frame.width,
                height=self.exp_stylized_dims.height,
            ),
        )


class PanelOutputTestCase(NamedTuple, Generic[ContentT]):
    content: ContentT
    frame: Frame | None
    config: OutputConfig | None
    exp_plain_output: str | None
    exp_dims: DimensionsWithWidthAndHeight
    exp_within_frame: WithinFrameExp


class StylizedPanelTestCaseSetup(NamedTuple, Generic[ContentT]):
    case_id: str
    content: ContentT
    frame: Frame | None = None
    config: OutputConfig | None = None


class StylizedPanelOutputExpectations(NamedTuple):
    get_output_property: OutputPropertyType
    exp_plain_output_for_case_id: Callable[[str], str]


# Functions


def get_exp_within_frame(
    frame: Frame | None,
    dims: DimensionsWithWidthAndHeight,
) -> WithinFrameExp:
    if frame is None:
        return WithinFrameExp(width=False, height=False, both=False)
    else:
        within_width = dims.width <= frame.dims.width if has_width(frame.dims) else None
        within_height = dims.height <= frame.dims.height if has_height(frame.dims) else None
        within_both = within_width and within_height if has_width(frame.dims) and has_height(
            frame.dims) else None
        return WithinFrameExp(width=within_width, height=within_height, both=within_both)


def apply_frame_variant_to_test_case(
    case: PanelFrameVariantTestCase,
    stylized_stage: bool,
) -> PanelOutputTestCase:
    assert not isinstance(case.exp_plain_output_only_width, pyd.UndefinedType)
    assert not isinstance(case.exp_resized_dims_only_width, pyd.UndefinedType)
    assert not isinstance(case.exp_stylized_dims_only_width, pyd.UndefinedType)
    assert not isinstance(case.exp_plain_output_only_height, pyd.UndefinedType)
    assert not isinstance(case.exp_resized_dims_only_height, pyd.UndefinedType)
    assert not isinstance(case.exp_stylized_dims_only_height, pyd.UndefinedType)
    assert not isinstance(case.exp_plain_output, pyd.UndefinedType)
    assert not isinstance(case.exp_resized_dims, pyd.UndefinedType)
    assert not isinstance(case.exp_stylized_dims, pyd.UndefinedType)

    if case.frame is None:  # no frame
        if case.frame_variant != FrameVariant(True, True):
            pytest.skip('Combination of no frame and only width/height is unnecessary.')

        return PanelOutputTestCase(
            content=case.content,
            frame=None,
            config=case.config,
            exp_plain_output=case.exp_plain_output_no_frame,
            exp_dims=case.exp_dims_all_stages_no_frame,
            exp_within_frame=WithinFrameExp(width=None, height=None, both=None),
        )
    else:
        match case.frame_variant:
            case True, False:  # only width
                frame_only_width = Frame(
                    Dimensions(width=case.frame.dims.width, height=None),
                    fixed_width=case.frame.fixed_width,
                )

                exp_dims_only_width = case.exp_stylized_dims_only_width if stylized_stage \
                    else case.exp_resized_dims_only_width

                return PanelOutputTestCase(
                    content=case.content,
                    frame=frame_only_width,
                    config=case.config,
                    exp_plain_output=case.exp_plain_output_only_width,
                    exp_dims=exp_dims_only_width,
                    exp_within_frame=get_exp_within_frame(frame_only_width, exp_dims_only_width),
                )
            case False, True:  # only height
                frame_only_height = Frame(
                    Dimensions(width=None, height=case.frame.dims.height),
                    fixed_height=case.frame.fixed_height,
                )

                exp_dims_only_height = case.exp_stylized_dims_only_height if stylized_stage \
                    else case.exp_resized_dims_only_height

                return PanelOutputTestCase(
                    content=case.content,
                    frame=frame_only_height,
                    config=case.config,
                    exp_plain_output=case.exp_plain_output_only_height,
                    exp_dims=exp_dims_only_height,
                    exp_within_frame=get_exp_within_frame(frame_only_height, exp_dims_only_height),
                )
            case True, True:  # width and height
                exp_plain_output = case.exp_plain_output
                exp_dims = case.exp_stylized_dims if stylized_stage else case.exp_resized_dims

                return PanelOutputTestCase(
                    content=case.content,
                    frame=case.frame,
                    config=case.config,
                    exp_plain_output=exp_plain_output,
                    exp_dims=exp_dims,
                    exp_within_frame=get_exp_within_frame(case.frame, exp_dims),
                )
        raise ShouldNotOccurException()


def create_draft_panel_kwargs(
    frame: Frame | None = None,
    constraints: Constraints | None = None,
    config: OutputConfig | None = None,
) -> DraftPanelKwArgs:
    kwargs = DraftPanelKwArgs()

    if frame is not None:
        kwargs['frame'] = frame

    if constraints is not None:
        kwargs['constraints'] = constraints

    if config is not None:
        kwargs['config'] = config

    return kwargs


def assert_draft_panel_subcls(
    panel_cls: type[DraftPanel],
    content: object,
    frame: Frame | None,
    constraints: Constraints | None,
    config: OutputConfig | None,
    content_is_identical: bool = True,
) -> None:
    kwargs = create_draft_panel_kwargs(frame, constraints, config)
    draft_panel = panel_cls(content, **kwargs)

    if frame is None:
        frame = empty_frame()

    if constraints is None:
        constraints = Constraints()

    if config is None:
        config = OutputConfig()

    if content_is_identical:
        assert draft_panel.content is content
    else:
        assert draft_panel.content is not content

    assert draft_panel.frame is not frame
    assert draft_panel.frame == frame, f'{draft_panel.frame} != {frame}'

    assert draft_panel.constraints is not constraints
    assert draft_panel.constraints == constraints, f'{draft_panel.constraints} != {constraints}'

    assert draft_panel.config is not config
    assert draft_panel.config == config, f'{draft_panel.config} != {config}'


def assert_dims_aware_panel(
    panel: DimensionsAwarePanel,
    exp_dims: DimensionsWithWidthAndHeight,
    exp_frame: Frame | None = None,
    exp_within_frame: WithinFrameExp | None = None,
) -> None:
    if exp_frame is None:
        exp_frame = Frame(Dimensions(width=None, height=None))
        exp_within_frame = WithinFrameExp(width=None, height=None, both=None)
    else:
        assert exp_frame is not None
        assert exp_within_frame is not None

    assert panel.dims.width == exp_dims.width, \
        f'{panel.dims.width} != {exp_dims.width}'
    assert panel.dims.height == exp_dims.height, \
        f'{panel.dims.height} != {exp_dims.height}'
    assert panel.frame.dims.width == exp_frame.dims.width, \
        f'{panel.frame.dims.width} != {exp_frame.dims.width}'
    assert panel.frame.dims.height == exp_frame.dims.height, \
        f'{panel.frame.dims.height} != {exp_frame.dims.height}'

    dims_fit = panel.within_frame
    assert dims_fit.width == exp_within_frame.width, \
        f'{dims_fit.width} != {exp_within_frame.width}'
    assert dims_fit.height == exp_within_frame.height, \
        f'{dims_fit.height} != {exp_within_frame.height}'
    assert dims_fit.both == exp_within_frame.both, \
        f'{dims_fit.both} != {exp_within_frame.both}'


def assert_next_stage_panel(
    this_panel: DraftPanel[object, FrameT],
    next_stage: Panel[FrameT],
    next_stage_panel_cls: type[DraftPanel[object, FrameT]],
    exp_content: object,
) -> None:
    assert isinstance(next_stage, next_stage_panel_cls)
    assert next_stage.content == exp_content, \
        f'{next_stage.content} != {exp_content}'
    assert next_stage.frame == this_panel.frame, \
        f'{next_stage.frame} != {this_panel.frame}'
    assert next_stage.constraints == this_panel.constraints, \
        f'{next_stage.constraints} != {this_panel.constraints}'
    assert next_stage.config == this_panel.config, \
        f'{next_stage.config} != {this_panel.config}'


def _strip_html(html: str) -> str:
    matches = re.findall(r'<code[^>]*>([\S\s]*)</code>', html, re.MULTILINE)
    if not matches:
        return html

    code_no_tags = re.sub(r'<[^>]+>', '', matches[0])

    def _to_char(match: re.Match) -> str:
        import sys
        byte_as_str = match[1]
        return int(byte_as_str, 16).to_bytes(length=1, byteorder=sys.byteorder).decode()

    code_no_escapes = re.sub(r'&#x(\d+);', _to_char, code_no_tags)
    return code_no_escapes


def _strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[^m]+m', '', text)


def strip_all_styling_from_panel_output(
    text_panel: SyntaxStylizedTextPanel | StylizedLayoutPanel,
    get_output_property: OutputPropertyType,
) -> str:
    return _strip_ansi(_strip_html(get_output_property(text_panel)))
