from typing import Any, Callable, TYPE_CHECKING

import solara

from omnipy.data._display.config import TERMINAL_DEFAULT_HEIGHT, TERMINAL_DEFAULT_WIDTH
from omnipy.shared.enums import ConsoleDimensionsMode

if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

_console_size = solara.reactive(dict(width=TERMINAL_DEFAULT_WIDTH, height=TERMINAL_DEFAULT_HEIGHT))


@solara.component_vue('getsize.vue')
def GetAvailableSize(font_weight: int,
                     font_size: int,
                     font_family: str,
                     line_height: float,
                     console_size: dict[str, int],
                     on_console_size: Callable[[dict[str, int]], None],
                     resize_delay: int = 20,
                     children=[],
                     style={}):
    ...


@solara.component
def ShowHtml(obj: 'Dataset | Model', console_size: dict[str, int], method_name: str, **kwargs: Any):

    if obj.config.display.jupyter.dims_mode is not ConsoleDimensionsMode.FIXED:
        obj.config.display.jupyter.width = console_size['width']
        obj.config.display.jupyter.height = console_size['height']

    html_string = getattr(obj, method_name)(**kwargs)

    solara.HTML(
        tag='div',
        unsafe_innerHTML=html_string,
    )


@solara.component
def DynamiclyResizingHtml(obj: 'Dataset | Model', method_name: str, **kwargs: Any):
    with GetAvailableSize(
            font_weight=obj.config.display.jupyter.font.weight,
            font_size=obj.config.display.jupyter.font.size,
            font_family=', '.join(
                f'"{family}"' for family in obj.config.display.jupyter.font.families),
            line_height=obj.config.display.jupyter.font.line_height,
            console_size=_console_size.value,
            on_console_size=_console_size.set,
    ):
        ShowHtml(
            obj,
            console_size=_console_size.value,
            method_name=method_name,
            **kwargs,
        )
