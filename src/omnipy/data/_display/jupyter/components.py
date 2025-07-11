from typing import Any, Callable, TYPE_CHECKING

import solara

from omnipy.shared.constants import TERMINAL_DEFAULT_HEIGHT, TERMINAL_DEFAULT_WIDTH
from omnipy.shared.enums.display import DisplayDimensionsUpdateMode

if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

# Overridden immediately by DynamiclyResizingHtml, so in practice not used unless there are issues
# with the Javascript component.
_available_display_dims = solara.reactive(
    dict(width=TERMINAL_DEFAULT_WIDTH, height=TERMINAL_DEFAULT_HEIGHT))


@solara.component_vue('getsize.vue')
def GetAvailableDisplayDims(font_weight: int,
                            font_size: int,
                            font_family: str,
                            line_height: float,
                            available_display_dims: dict[str, int],
                            on_available_display_dims: Callable[[dict[str, int]], None],
                            resize_delay: int = 20,
                            children=[],
                            style={}):
    ...


@solara.component
def ShowHtml(obj: 'Dataset | Model',
             available_display_dims: dict[str, int],
             method_name: str,
             **kwargs: Any):

    if obj.config.ui.jupyter.dims_mode is not DisplayDimensionsUpdateMode.FIXED:
        obj.config.ui.jupyter.width = available_display_dims['width']
        obj.config.ui.jupyter.height = available_display_dims['height']

    html_string = getattr(obj, method_name)(**kwargs)

    solara.HTML(
        tag='div',
        unsafe_innerHTML=html_string,
    )


@solara.component
def DynamiclyResizingHtml(obj: 'Dataset | Model', method_name: str, **kwargs: Any):
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
            available_display_dims=_available_display_dims.value,
            method_name=method_name,
            **kwargs,
        )
