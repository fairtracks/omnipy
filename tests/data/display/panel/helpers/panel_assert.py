import re
from textwrap import dedent
from typing import TypedDict

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.base import DimensionsAwarePanel, Panel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
from omnipy.data._display.panel.typedefs import FrameT

from .case_setup import OutputPropertyType, WithinFrameExp


class DraftPanelKwArgs(TypedDict, total=False):
    frame: Frame
    title: str
    constraints: Constraints
    config: OutputConfig


def create_draft_panel_kwargs(
    frame: Frame | None = None,
    title: str = '',
    constraints: Constraints | None = None,
    config: OutputConfig | None = None,
) -> DraftPanelKwArgs:
    kwargs = DraftPanelKwArgs()

    if frame is not None:
        kwargs['frame'] = frame

    if title != '':
        kwargs['title'] = title

    if constraints is not None:
        kwargs['constraints'] = constraints

    if config is not None:
        kwargs['config'] = config

    return kwargs


def assert_draft_panel_subcls(
    panel_cls: type[DraftPanel],
    content: object,
    frame: Frame | None = None,
    title: str = '',
    constraints: Constraints | None = None,
    config: OutputConfig | None = None,
    content_is_identical: bool = True,
) -> None:
    kwargs = create_draft_panel_kwargs(frame, title, constraints, config)
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

    assert draft_panel.title == title, f'{draft_panel.title} != {title}'

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

    assert panel.dims.width == exp_dims.width, \
        f'{panel.dims.width} != {exp_dims.width}'
    assert panel.dims.height == exp_dims.height, \
        f'{panel.dims.height} != {exp_dims.height}'
    assert panel.frame.dims.width == exp_frame.dims.width, \
        f'{panel.frame.dims.width} != {exp_frame.dims.width}'
    assert panel.frame.dims.height == exp_frame.dims.height, \
        f'{panel.frame.dims.height} != {exp_frame.dims.height}'

    if exp_within_frame is not None:
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
        f'\n{next_stage.content} != \n{exp_content}'
    assert next_stage.frame == this_panel.frame, \
        f'\n{next_stage.frame} != \n{this_panel.frame}'
    assert next_stage.title == this_panel.title, \
        f'\n{next_stage.title} != \n{this_panel.title}'
    assert next_stage.constraints == this_panel.constraints, \
        f'\n{next_stage.constraints} != \n{this_panel.constraints}'
    assert next_stage.config == this_panel.config, \
        f'\n{next_stage.config} != \n{this_panel.config}'


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


def _get_font_style_by_case_id(case_id: str | None) -> str:
    DEFAULT_FONT_STYLE = (
        "font-family: 'CommitMonoOmnipy', 'Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', "
        "'monospace'; font-size: 14px; font-weight: 450; line-height: 1.35; ")

    FONT_STYLING_ONLY = 'font-weight: 500; line-height: 1.0; '

    FULL_FONT_CONF = ("font-family: 'monospace'; font-size: 15px; "
                      'font-weight: 600; line-height: 1.1; ')

    match (case_id):
        case str(case_id) if 'no-fonts' in case_id:
            return ''
        case str(case_id) if 'font-styling-only' in case_id:
            return FONT_STYLING_ONLY
        case str(case_id) if 'full-font-conf' in case_id:
            return FULL_FONT_CONF
        case _:
            return DEFAULT_FONT_STYLE


def fill_html_tag_template(data: str, color_style: str = '', case_id: str | None = None) -> str:
    HTML_TAG_TEMPLATE = ('<pre>'
                         '<code style="{font_style}{color_style}">'
                         '{data}\n'
                         '</code>'
                         '</pre>')

    return HTML_TAG_TEMPLATE.format(
        font_style=_get_font_style_by_case_id(case_id),
        color_style=color_style,
        data=data,
    )


def fill_html_page_template(style: str, data: str, case_id: str | None = None) -> str:
    HTML_PAGE_TEMPLATE = dedent("""\
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <style>
              {style}
            </style>
          </head>
          <body>
            <pre><code style="{font_style}">{data}
        </code></pre>
          </body>
        </html>
        """)

    return HTML_PAGE_TEMPLATE.format(
        style=style,
        font_style=_get_font_style_by_case_id(case_id),
        data=data,
    )
