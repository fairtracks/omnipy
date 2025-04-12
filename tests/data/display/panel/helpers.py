import re
from typing import Callable, Generic, TypeAlias, TypedDict

import pytest
from typing_extensions import NamedTuple, TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import empty_frame, Frame, FrameWithWidthAndHeight
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT, Panel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
from omnipy.shared.exceptions import ShouldNotOccurException

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


class WithinFrameExpCase(NamedTuple):
    width: bool | None
    height: bool | None
    both: bool | None


class FrameTestCase(NamedTuple):
    frame: Frame | None
    exp_dims: DimensionsWithWidthAndHeight
    exp_within_frame: WithinFrameExpCase




class PanelOutputTestCase(NamedTuple, Generic[ContentT]):
    content: ContentT
    frame: Frame | None
    config: OutputConfig | None
    exp_output: str
    exp_dims: DimensionsWithWidthAndHeight
    exp_within_frame: WithinFrameExp


class PanelOutputFrameVariantTestCase(NamedTuple, Generic[ContentT]):
    content: ContentT
    frame: FrameWithWidthAndHeight | None
    config: OutputConfig | None
    exp_output: str
    exp_dims: DimensionsWithWidthAndHeight
    exp_within_frame: WithinFrameExp
    frame_variant: FrameVariant
    cropping_frame_exp_output: str
    cropping_frame_exp_dims: DimensionsWithWidthAndHeight
    cropping_frame_exp_within_frame: WithinFrameExp


class PanelOutputTestCaseSetup(NamedTuple, Generic[ContentT]):
    case_id: str
    content: ContentT
    frame: Frame | None = None
    config: OutputConfig | None = None


class PanelOutputPropertyExpectations(NamedTuple):
    get_output_property: OutputPropertyType
    expected_output_for_case_id: Callable[[str], str]


# Functions


def frame_smaller_than_dims(
    frame: FrameWithWidthAndHeight | None,
    dims: DimensionsWithWidthAndHeight,
) -> bool:
    if frame is None:
        return False
    else:
        return frame.dims.width < dims.width or frame.dims.height < dims.height


def apply_frame_variant_to_test_case(
    case: PanelOutputFrameVariantTestCase,
    crop_to_frame: bool,
) -> FrameTestCase:
    if case.frame is None:
        if case.frame_variant != FrameVariant(True, True):
            pytest.skip('Combination of no frame and only width/height is unnecessary.')

        assert case.exp_within_frame.width is None
        assert case.exp_within_frame.height is None

        return FrameTestCase(
            frame=None,
            exp_dims=case.exp_dims,
            exp_within_frame=WithinFrameExpCase(width=None, height=None, both=None),
        )
    else:
        new_exp_dims = case.cropping_frame_exp_dims if crop_to_frame else case.exp_dims
        new_exp_within_frame = case.cropping_frame_exp_within_frame if crop_to_frame \
            else case.exp_within_frame

        match case.frame_variant:
            case True, False:
                return FrameTestCase(
                    frame=Frame(Dimensions(width=case.frame.dims.width, height=None)),
                    exp_dims=Dimensions(width=new_exp_dims.width, height=case.exp_dims.height),
                    exp_within_frame=WithinFrameExpCase(
                        width=new_exp_within_frame.width, height=None, both=None),
                )
            case False, True:
                return FrameTestCase(
                    frame=Frame(Dimensions(width=None, height=case.frame.dims.height)),
                    exp_dims=Dimensions(width=case.exp_dims.width, height=new_exp_dims.height),
                    exp_within_frame=WithinFrameExpCase(
                        width=None, height=new_exp_within_frame.height, both=None),
                )
            case True, True:
                return FrameTestCase(
                    frame=case.frame,
                    exp_dims=new_exp_dims,
                    exp_within_frame=WithinFrameExpCase(
                        width=new_exp_within_frame.width,
                        height=new_exp_within_frame.height,
                        both=new_exp_within_frame.width and new_exp_within_frame.height,
                    ),
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
) -> None:
    kwargs = create_draft_panel_kwargs(frame, constraints, config)
    draft_panel = panel_cls(content, **kwargs)

    if frame is None:
        frame = empty_frame()

    if constraints is None:
        constraints = Constraints()

    if config is None:
        config = OutputConfig()

    assert draft_panel.content is content

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
    exp_within_frame: WithinFrameExpCase | None = None,
) -> None:
    if exp_frame is None:
        exp_frame = Frame(Dimensions(width=None, height=None))
        exp_within_frame = WithinFrameExpCase(width=None, height=None, both=None)
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
