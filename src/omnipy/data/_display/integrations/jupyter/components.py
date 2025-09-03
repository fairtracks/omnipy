import re
from typing import Any, Callable, ParamSpec, TYPE_CHECKING

import solara

from omnipy.data._display.panel.helpers import is_color_dark
from omnipy.shared.enums.display import DisplayDimensionsUpdateMode
from omnipy.shared.protocols.config import IsJupyterUserInterfaceConfig
from omnipy.shared.protocols.data import IsReactiveObjects
from omnipy.shared.typedefs import Method
from omnipy.util import _pydantic as pyd

if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

P = ParamSpec('P')

_RGB_REGEXP = re.compile(r'rgb\( *(\d+), *(\d+), *(\d+) *\)')


class AvailableDisplayDims(dict[str, pyd.NonNegativeInt | None]):
    ...


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
def ReactiveBgColorUpdater(jupyter_ui_config: IsJupyterUserInterfaceConfig):
    _bg_color = solara.use_reactive('')

    with GetPageBgColor(
            bg_color=_bg_color.value,
            on_bg_color=_bg_color.set,
    ):
        jupyter_ui_config.color.dark_background = _is_dark_background(_bg_color.value)


@solara.component_vue('getsize.vue')
def GetAvailableDisplayDims(
    font_weight: int,
    font_size: int,
    font_family: str,
    line_height: float,
    available_display_dims: AvailableDisplayDims,
    on_available_display_dims: Callable[[AvailableDisplayDims], None],
    resize_delay: int = 20,
    children=[],
    style={},
):
    ...


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ShowHtml(
    jupyter_ui_config: IsJupyterUserInterfaceConfig,
    output_method: Method[P, str],
    *args: Any,
    **kwargs: Any,
):
    solara.HTML(
        tag='div',
        unsafe_innerHTML=output_method(*args, **kwargs),
    )


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactiveAvailableDisplaySizeUpdater(
    jupyter_ui_config: IsJupyterUserInterfaceConfig,
    reactive_objects: IsReactiveObjects,
):
    reactive_jupyter_ui_config = reactive_objects.jupyter_ui_config.value

    def get_available_display_dims() -> AvailableDisplayDims:
        return AvailableDisplayDims(
            width=reactive_jupyter_ui_config.width,
            height=reactive_jupyter_ui_config.height,
        )

    def set_available_display_dims(available_display_dims):
        if jupyter_ui_config.dims_mode is not DisplayDimensionsUpdateMode.FIXED:
            jupyter_ui_config.width = available_display_dims['width']
            jupyter_ui_config.height = available_display_dims['height']

    GetAvailableDisplayDims(
        font_weight=reactive_jupyter_ui_config.font.weight,
        font_size=reactive_jupyter_ui_config.font.size,
        font_family=', '.join(f'"{family}"' for family in reactive_jupyter_ui_config.font.families),
        line_height=reactive_jupyter_ui_config.font.line_height,
        available_display_dims=get_available_display_dims(),
        on_available_display_dims=set_available_display_dims,
    )


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactivelyResizingHtml(
    obj: 'Dataset | Model',
    output_method: Method[P, str],  # available_display_dims: AvailableDisplayDims,
    *args: Any,
    **kwargs: Any,
):
    ShowHtml(
        jupyter_ui_config=obj.reactive_objects.jupyter_ui_config.value,
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
    html_content: dict[str, str],
    children=[],
    style={},
):
    ...
