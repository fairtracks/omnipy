from dataclasses import dataclass, field
from typing import Annotated, Callable, cast, Generic, TypeAlias

import pytest
import pytest_cases as pc
from typing_extensions import NamedTuple, TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width)
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.base import FrameT
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd

OutputPropertyType: TypeAlias = Callable[[SyntaxStylizedTextPanel | StylizedLayoutPanel], str]
ContentT = TypeVar('ContentT', bound=str | Layout)

# Classes


class FrameVariant(NamedTuple):
    use_frame_width: bool
    use_frame_height: bool


class WithinFrameExp(NamedTuple):
    width: bool | None
    height: bool | None
    both: bool | None


@dataclass
class FrameTestCase(Generic[ContentT, FrameT]):
    frame: FrameT | None
    content: ContentT | pyd.UndefinedType = field(default=pyd.Undefined)
    config: OutputConfig | None | pyd.UndefinedType = field(default=pyd.Undefined)

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
    exp_plain_output_no_frame: str | None
    exp_dims_all_stages_no_frame: DimensionsWithWidthAndHeight
    frame_case: FrameTestCase[ContentT, FrameT]
    frame_variant: FrameVariant
    title: str = ''
    config: OutputConfig | None | pyd.UndefinedType = field(default=pyd.Undefined)

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
        self.frame = self.frame_case.frame
        self.content = cast(ContentT,
                            _resolve_to_first_defined(
                                self.frame_case.content,
                                self.content,
                            ))

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
        self.config = _resolve_to_first_defined(
            self.frame_case.config,
            self.config,
            None,
        )


class PanelOutputTestCase(NamedTuple, Generic[ContentT]):
    content: ContentT
    frame: Frame | None
    config: OutputConfig | None
    exp_plain_output: str | None
    exp_dims: DimensionsWithWidthAndHeight
    exp_within_frame: WithinFrameExp
    title: str = ''


class StylizedPanelTestCaseSetup(NamedTuple, Generic[ContentT]):
    case_id: str
    content: ContentT
    title: str = ''
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
    assert not isinstance(case.config, pyd.UndefinedType)
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


def prepare_test_case_for_stylized_layout(
    case: PanelOutputTestCase[Layout] | PanelFrameVariantTestCase[Layout],
    plain_terminal: Annotated[OutputPropertyType, pc.fixture],
    output_format_accessor: Annotated[OutputPropertyType, pc.fixture],
) -> PanelOutputTestCase[Layout]:
    if isinstance(case, PanelFrameVariantTestCase):
        if case.frame_variant != FrameVariant(True, True) \
                and output_format_accessor != plain_terminal:
            pytest.skip('Skip test combination to increase test efficiency.')

        case = apply_frame_variant_to_test_case(case, stylized_stage=True)
    return case
