import re
from typing import Any, Callable, ParamSpec, TYPE_CHECKING

import solara

from omnipy.data._display.panel.helpers import is_color_dark
from omnipy.shared.constants import TERMINAL_DEFAULT_HEIGHT, TERMINAL_DEFAULT_WIDTH
from omnipy.shared.enums.display import DisplayDimensionsUpdateMode
from omnipy.shared.protocols.config import IsColorConfig
from omnipy.shared.typedefs import Method

if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

P = ParamSpec('P')

# Overridden immediately by ReactivelyResizingHtml, so in practice not used unless there are issues
# with the Javascript component.
_available_display_dims = solara.reactive(
    dict(width=TERMINAL_DEFAULT_WIDTH, height=TERMINAL_DEFAULT_HEIGHT))

_bg_color = solara.reactive('')

_RGB_REGEXP = re.compile(r'rgb\( *(\d+), *(\d+), *(\d+) *\)')


def _is_dark_background(bg_color: str) -> bool:
    """
    Determines whether the background color is dark based on the RGB values in the string.
    """
    match = _RGB_REGEXP.match(bg_color)
    if match:
        red, green, blue = map(int, match.groups())
        return is_color_dark(red, green, blue)
    return False


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactiveBgColorUpdater(color_config: IsColorConfig):
    with GetPageBgColor(
            bg_color=_bg_color.value,
            on_bg_color=_bg_color.set,
    ):
        color_config.dark_background = _is_dark_background(_bg_color.value)


@solara.component_vue('getsize.vue')
def GetAvailableDisplayDims(
    font_weight: int,
    font_size: int,
    font_family: str,
    line_height: float,
    available_display_dims: dict[str, int],
    on_available_display_dims: Callable[[dict[str, int]], None],
    resize_delay: int = 20,
    children=[],
    style={},
):
    ...


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ShowHtml(
    obj: 'Dataset | Model',
    bg_color: str,
    available_display_dims: dict[str, int],
    output_method: Method[P, str],
    *args: Any,
    **kwargs: Any,
):

    if obj.config.ui.jupyter.dims_mode is not DisplayDimensionsUpdateMode.FIXED:
        obj.config.ui.jupyter.width = available_display_dims['width']
        obj.config.ui.jupyter.height = available_display_dims['height']

    obj.config.ui.jupyter.color.dark_background = _is_dark_background(bg_color)
    html_string = output_method(*args, **kwargs)

    solara.HTML(
        tag='div',
        unsafe_innerHTML=html_string,
        classes=[str(obj.config.ui.jupyter.color.dark_background)],
    )


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactivelyResizingHtml(
    obj: 'Dataset | Model',
    output_method: Method[P, str],
    *args: Any,
    **kwargs: Any,
):
    with GetAvailableDisplayDims(
            font_weight=obj.config.ui.jupyter.font.weight,
            font_size=obj.config.ui.jupyter.font.size,
            font_family=', '.join(f'"{family}"' for family in obj.config.ui.jupyter.font.families),
            line_height=obj.config.ui.jupyter.font.line_height,
            available_display_dims=_available_display_dims.value,
            on_available_display_dims=_available_display_dims.set,
    ):
        ShowHtml(
            obj,
            bg_color=_bg_color.value,
            available_display_dims=_available_display_dims.value,
            output_method=output_method,
            *args,
            **kwargs,
        )


@solara.component_vue('getpagebgcolor.vue')
def GetPageBgColor(
    bg_color: str,
    on_bg_color: Callable[[str], None],
    update_delay: int = 100,
    children=[],
    style={},
):
    ...


@solara.component_vue('browse.vue')
def BrowseModels(
    html_contents: dict[str, str],
    children=[],
    style={},
):
    ...
