import re
from typing import Any, Callable, ParamSpec, TYPE_CHECKING

import solara

from omnipy.data._display.panel.base import FullyRenderedPanel
from omnipy.data._display.panel.helpers import is_color_dark
from omnipy.shared.enums.display import DisplayDimensionsUpdateMode
from omnipy.shared.protocols.config import (IsJupyterUserInterfaceConfig,
                                            IsLayoutConfig,
                                            IsTextConfig)
from omnipy.shared.protocols.data import AvailableDisplayDims, IsReactiveObjects

if TYPE_CHECKING:
    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

P = ParamSpec('P')

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


def _comma_join_fonts(families: tuple[str, ...]) -> str:
    return ', '.join(f'"{family}"' for family in families)


def _get_available_display_dims(
        reactive_jupyter_ui_config: IsJupyterUserInterfaceConfig) -> AvailableDisplayDims:
    return AvailableDisplayDims(
        width=reactive_jupyter_ui_config.width,
        height=reactive_jupyter_ui_config.height,
    )


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactiveBgColorUpdater(jupyter_ui_config: IsJupyterUserInterfaceConfig):
    _bg_color = solara.use_reactive('')

    with PageBgColorDetector(
            bg_color=_bg_color.value,
            on_bg_color=_bg_color.set,
    ):
        if jupyter_ui_config.color.dark_background != _is_dark_background(_bg_color.value):
            jupyter_ui_config.color.dark_background = _is_dark_background(_bg_color.value)


@solara.component_vue('AvailableDisplayDimsDetector.vue')
def AvailableDisplayDimsDetector(
    available_display_dims_in_px: AvailableDisplayDims,
    on_available_display_dims_in_px: Callable[[AvailableDisplayDims], None],
    resize_delay: int = 20,
    children=[],
    style={},
):
    ...


@solara.component_vue('DimsCalculator.vue')
def DimsCalculator(
    available_display_dims_in_px: AvailableDisplayDims,
    available_display_dims: AvailableDisplayDims,
    on_available_display_dims: Callable[[AvailableDisplayDims], None],
    font_weight: int,
    font_size: int,
    font_family: str,
    line_height: float,
    children=[],
    style={},
):
    ...


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ShowHtml(
    jupyter_ui_config: IsJupyterUserInterfaceConfig,
    orig_jupyter_ui_config: IsJupyterUserInterfaceConfig,
    text_config: IsTextConfig,
    orig_text_config: IsTextConfig,
    layout_config: IsLayoutConfig,
    orig_layout_config: IsLayoutConfig,
    rendered_panel: FullyRenderedPanel,
    render_panel_method: Callable[..., FullyRenderedPanel],
    render_output_method: Callable[[FullyRenderedPanel], str],
    **kwargs: Any,
):
    if (jupyter_ui_config != orig_jupyter_ui_config or text_config != orig_text_config
            or layout_config != orig_layout_config):
        rendered_panel = render_panel_method(**kwargs)

    solara.HTML(
        tag='div',
        unsafe_innerHTML=render_output_method(rendered_panel),
    )


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactiveAvailableDisplaySizeUpdater(
    jupyter_ui_config: IsJupyterUserInterfaceConfig,
    reactive_objects: IsReactiveObjects,
):
    reactive_jupyter_ui_config = reactive_objects.jupyter_ui_config.value

    def _set_available_display_dims(available_display_dims: AvailableDisplayDims):
        if jupyter_ui_config.dims_mode is not DisplayDimensionsUpdateMode.FIXED:
            jupyter_ui_config.set_width_and_height(
                available_display_dims['width'],
                available_display_dims['height'],
            )

    with AvailableDisplayDimsDetector(
            available_display_dims_in_px=reactive_objects.available_display_dims_in_px.value,
            on_available_display_dims_in_px=reactive_objects.available_display_dims_in_px.set,
    ):
        DimsCalculator(
            available_display_dims_in_px=reactive_objects.available_display_dims_in_px.value,
            available_display_dims=_get_available_display_dims(reactive_jupyter_ui_config),
            on_available_display_dims=_set_available_display_dims,
            font_weight=reactive_jupyter_ui_config.font.weight,
            font_size=reactive_jupyter_ui_config.font.size,
            font_family=_comma_join_fonts(reactive_jupyter_ui_config.font.families),
            line_height=reactive_jupyter_ui_config.font.line_height,
        )


@solara.component  # pyright: ignore [reportPrivateImportUsage]
def ReactivelyResizingHtml(
    obj: 'Dataset | Model',
    orig_jupyter_ui_config: IsJupyterUserInterfaceConfig,
    orig_text_config: IsTextConfig,
    orig_layout_config: IsLayoutConfig,
    rendered_panel: FullyRenderedPanel,
    render_panel_method: Callable[..., FullyRenderedPanel],
    render_output_method: Callable[[FullyRenderedPanel], str],
    reactive_kwargs: solara.Reactive[dict[str, Any]],
):
    kwargs = reactive_kwargs.value
    reactive_objs = obj.reactive_objects
    reactive_jupyter_ui_config = reactive_objs.jupyter_ui_config.value
    reactive_text_config = reactive_objs.text_config.value
    reactive_layout_config = reactive_objs.layout_config.value

    if any(_ in kwargs for _ in ('font_weight', 'font_size', 'fonts', 'line_height')):

        def _set_width_and_height_in_kwargs(available_display_dims: AvailableDisplayDims):
            kwargs_copy = kwargs.copy()
            kwargs_copy['width'] = available_display_dims['width']
            kwargs_copy['height'] = available_display_dims['height']
            reactive_kwargs.set(kwargs_copy)

        with DimsCalculator(
                available_display_dims_in_px=reactive_objs.available_display_dims_in_px.value,
                available_display_dims=_get_available_display_dims(reactive_jupyter_ui_config),
                on_available_display_dims=_set_width_and_height_in_kwargs,
                font_weight=kwargs.get('font_weight') or reactive_jupyter_ui_config.font.weight,
                font_size=kwargs.get('font_size') or reactive_jupyter_ui_config.font.size,
                font_family=_comma_join_fonts(
                    kwargs.get('fonts') or reactive_jupyter_ui_config.font.families),
                line_height=(kwargs.get('line_height')
                             or reactive_jupyter_ui_config.font.line_height),
        ):
            if 'width' in kwargs and 'height' in kwargs:
                # re-render panel as dims most probably have changed
                rendered_panel = render_panel_method(**kwargs)

    ShowHtml(
        jupyter_ui_config=reactive_jupyter_ui_config,
        orig_jupyter_ui_config=orig_jupyter_ui_config,
        text_config=reactive_text_config,
        orig_text_config=orig_text_config,
        layout_config=reactive_layout_config,
        orig_layout_config=orig_layout_config,
        rendered_panel=rendered_panel,
        render_panel_method=render_panel_method,
        render_output_method=render_output_method,
        **kwargs)


@solara.component_vue('PageBgColorDetector.vue')
def PageBgColorDetector(
    bg_color: str,
    on_bg_color: Callable[[str], None],
    update_delay: int = 100,
    children=[],
    style={},
):
    ...


@solara.component_vue('ModelBrowser.vue')
def ModelBrowser(
    html_content: dict[str, str],
    children=[],
    style={},
):
    ...
