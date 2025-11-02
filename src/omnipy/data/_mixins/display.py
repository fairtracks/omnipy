from abc import ABCMeta, abstractmethod
import dataclasses
import functools
import os
from pathlib import Path
import sys
from typing import Any, cast, Literal, overload, ParamSpec, TYPE_CHECKING
import webbrowser

from pathvalidate import sanitize_filename
import solara
from typing_extensions import assert_never, get_args, LiteralString, TypeVar

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions, has_height, has_width
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.integrations.browser.macosx import (OmnipyMacOSXOSAScript,
                                                              setup_macosx_browser_integration)
from omnipy.data._display.layout.base import Layout, PanelDesignDims
from omnipy.data._display.panel.base import FullyRenderedPanel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data.helpers import FailedData, PendingData
from omnipy.hub.ui import get_terminal_prompt_height, note_mime_bundle
from omnipy.shared.constants import TITLE_BLANK_LINES
from omnipy.shared.enums.colorstyles import AllColorStyles, RecommendedColorStyles
from omnipy.shared.enums.display import (DisplayColorSystem,
                                         MaxTitleHeight,
                                         PanelDesign,
                                         SyntaxLanguage)
from omnipy.shared.enums.ui import (BrowserPageUserInterfaceType,
                                    BrowserTagUserInterfaceType,
                                    BrowserUserInterfaceType,
                                    JupyterEmbeddedUserInterfaceType,
                                    JupyterInBrowserUserInterfaceType,
                                    SpecifiedUserInterfaceType,
                                    TerminalOutputUserInterfaceType,
                                    UserInterfaceType)
from omnipy.shared.protocols.config import IsHtmlUserInterfaceConfig, IsUserInterfaceTypeConfig
from omnipy.shared.typedefs import Method, TypeForm
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import takes_input_params_from

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter
    from reacton.core import Element

    from omnipy.data.dataset import Dataset
    from omnipy.data.model import Model

if sys.platform == 'darwin':
    # Register the macOS browser integration for webbrowser module
    setup_macosx_browser_integration()

P = ParamSpec('P')
LiteralT = TypeVar('LiteralT', bound=LiteralString)


@pyd.dataclass(
    kw_only=True,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class _DimsRestatedParams:
    """
    NOTE: Only used to generate parameter lists, not a real dataclass
    """
    width: pyd.NonNegativeInt | None = None
    height: pyd.NonNegativeInt | None = None


@pyd.dataclass(
    kw_only=True,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class _DisplayMethodParams(OutputConfig, _DimsRestatedParams):
    """
    NOTE: Only used to generate parameter lists, not a real dataclass
    """
    ...


class BaseDisplayMixin(metaclass=ABCMeta):
    @abstractmethod
    def _default_panel(self, **kwargs) -> DraftPanel:
        ...

    def default_repr_to_terminal_str(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals,
    ) -> str:
        return self._display_according_to_ui_type(
            ui_type=ui_type,
            return_output_if_str=True,
            output_method=self._default_panel,
        )

    @takes_input_params_from(_DisplayMethodParams.__init__)
    def peek(self, **kwargs) -> 'Element | None':
        """
        Displays a preview of the model or dataset. For models, this is a
        preview of the model's content, and for datasets, this is a
        side-by-side view of each model contained in the dataset. Both views
        are automatically limited by the available display dimensions.
        :return: If the UI type is Jupyter running in a browser, `peek`
        returns a ReactivelyResizingHtml element which is a Jupyter widget
        to display HTML output in the browser. Otherwise, returns None.
        """
        return self._display_according_to_ui_type(
            ui_type=self._extract_ui_type(**kwargs),
            return_output_if_str=False,
            output_method=self._peek,
            **kwargs,
        )

    def _extract_ui_type(self, **kwargs) -> SpecifiedUserInterfaceType.Literals:
        return (kwargs.get('ui', None) or cast(DataClassBase, self).config.ui.detected_type)

    @classmethod
    def _prepare_kwargs_for_full(cls, kwargs):
        kwargs_copy = kwargs.copy()
        kwargs_copy['height'] = None
        return kwargs_copy

    @takes_input_params_from(_DisplayMethodParams.__init__)
    def full(self, **kwargs) -> 'Element | None':
        """
        Displays a full-height version of the default representation of the
        model or dataset. This is the same as `peek(height=None)` for
        models, and `list(height=None)` for datasets. Both views
        are automatically limited in width by the available display
        dimensions.
        :return: If the UI type is Jupyter runnint in in browser, `peek`
        returns a ReactivelyResizingHtml element which is a Jupyter widget
        to display HTML output in the browser. Otherwise, returns None.
        """
        return self._display_according_to_ui_type(
            ui_type=self._extract_ui_type(**kwargs),
            return_output_if_str=False,
            output_method=self._full,
            **kwargs)

    @takes_input_params_from(_DisplayMethodParams.__init__)
    def browse(self, **kwargs) -> None:
        """
        Opens the model or dataset in a browser, if possible. For models,
        this is a detailed view of the model's content, and for datasets
        this is a detailed view of each model contained in the dataset,
        one model per browser tab.
        """
        self._browse(**kwargs)

    @abstractmethod
    def _peek(self, **kwargs) -> DraftPanel:
        ...

    @abstractmethod
    def _full(self, **kwargs) -> DraftPanel:
        ...

    @abstractmethod
    def _browse(self, **kwargs) -> None:
        ...

    @takes_input_params_from(_DisplayMethodParams.__init__)
    def _docs(self, **kwargs) -> str:
        """
        Displays a preview of the model or dataset for the documentation.
        """
        ui_type = UserInterfaceType.BROWSER_TAG
        if 'style' not in kwargs:
            kwargs['style'] = RecommendedColorStyles.OMNIPY_SELENIZED_WHITE
        if 'ui' not in kwargs:
            kwargs['ui'] = ui_type

        return self._display_according_to_ui_type(
            ui_type=ui_type,
            return_output_if_str=True,
            output_method=self._default_panel,
            **kwargs,
        )

    def __str__(self) -> str:
        return repr(self)

    def _repr_pretty_(self, p: 'RepresentationPrinter', cycle: bool) -> None:
        if cycle:
            # __repr_pretty__ called recursively. The ellipsis stops the
            # recursion.
            p.text(f'{cast(pyd.GenericModel, self).__repr_name__()}(...)')
        else:
            # as panels.
            if len(p.stack) == 1:
                # The Model or Dataset object is at the top level and should
                # be displayed.
                ui_type = cast(DataClassBase, self).config.ui.detected_type
                if UserInterfaceType.is_jupyter(ui_type):
                    # Jupyter calls both _repr_pretty_() and _repr_html_(),
                    # so we ignore the _repr_pretty_ call and instead
                    # provide the output in _repr_html_().
                    return

                output: str = self._display_according_to_ui_type(
                    ui_type=ui_type,
                    return_output_if_str=True,
                    output_method=self._default_panel,
                )
                p.text(output)
            else:
                # The Model or Dataset object is nested inside another
                # object, so we display its basic __repr__() instead.
                # TODO: Add basic styling also to nested Model or Dataset
                #       __repr__()?
                p.text(self.__repr__())

    def _ipython_display_(self) -> None:
        ui_type = cast(DataClassBase, self).config.ui.detected_type
        if UserInterfaceType.is_ipython_terminal(ui_type):
            print()  # Otherwise, first line is indented due to prompt
        self._display_according_to_ui_type(
            ui_type=ui_type,
            return_output_if_str=False,
            output_method=self._default_panel,
        )

    @overload
    def _display_according_to_ui_type(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals | BrowserUserInterfaceType.Literals,
        return_output_if_str: Literal[True],
        output_method: Method[P, DraftPanel],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str:
        ...

    @overload
    def _display_according_to_ui_type(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals | BrowserUserInterfaceType.Literals,
        return_output_if_str: Literal[False],
        output_method: Method[P, DraftPanel],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        ...

    @overload
    def _display_according_to_ui_type(
        self,
        ui_type: JupyterInBrowserUserInterfaceType.Literals,
        return_output_if_str: bool,
        output_method: Method[P, DraftPanel],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        ...

    def _display_according_to_ui_type(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
        return_output_if_str: bool,
        output_method: Method[P, DraftPanel],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> 'str | Element | None':
        def _render_panel(
            ui_type: SpecifiedUserInterfaceType.Literals,
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> FullyRenderedPanel:
            panel = output_method(*args, **kwargs)
            resized_panel = panel.render_next_stage()
            if ui_type in BrowserPageUserInterfaceType:
                # If the output is a browser page, we allow expanding the
                # frame to fit the content
                if not resized_panel.within_frame.width:
                    wider_panel = dataclasses.replace(
                        panel,
                        frame=panel.frame.modified_copy(width=resized_panel.dims.width),
                    )
                    resized_panel = wider_panel.render_next_stage()
            return resized_panel.render_next_stage()

        def _render_output(
            rendered_panel: FullyRenderedPanel,
            ui_type: SpecifiedUserInterfaceType.Literals,
        ) -> str:
            match ui_type:
                case x if UserInterfaceType.requires_terminal_output(x):
                    return rendered_panel.colorized.terminal
                case x if UserInterfaceType.requires_html_tag_output(x):
                    return rendered_panel.colorized.html_tag
                case x if UserInterfaceType.requires_html_page_output(x):
                    return rendered_panel.colorized.html_page
                case _ as never:
                    # Only supported by mypy, see https://github.com/microsoft/pyright/issues/10680
                    assert_never(never)  # pyright: ignore [reportArgumentType]

        match ui_type:
            case x if UserInterfaceType.is_jupyter(x):
                mime_bundle = {}

                embedded_ui_type = get_args(JupyterEmbeddedUserInterfaceType.Literals)[0]
                rendered_panel = _render_panel(embedded_ui_type, *args, **kwargs)
                mime_bundle['text/plain'] = _render_output(rendered_panel, embedded_ui_type)

                if UserInterfaceType.is_jupyter_in_browser(ui_type):
                    import reacton
                    from reacton.core import Element

                    from omnipy.data._display.integrations.jupyter.components import \
                        ReactivelyResizingHtml

                    browser_tag_ui_type = BrowserTagUserInterfaceType.BROWSER_TAG

                    mime_bundle = note_mime_bundle(
                        bullet='⚠️',
                        html_content=('Widget for reactive Omnipy output '
                                      'was not loaded. If you are running '
                                      'Jupyter in a web browser, you '
                                      'probably want to rerun the code '
                                      'cell above (<i>Click in the code '
                                      'cell, and press Shift+Enter '
                                      '<kbd>⇧</kbd>+<kbd>↩</kbd></i>).'),
                    )
                    mime_bundle['text/html'] += _render_output(rendered_panel, browser_tag_ui_type)

                    self_as_dataclass = cast('Dataset | Model', self)
                    element: Element = ReactivelyResizingHtml(
                        self_as_dataclass,
                        self_as_dataclass.config.ui.jupyter.deepcopy(),
                        self_as_dataclass.config.ui.text.deepcopy(),
                        self_as_dataclass.config.ui.layout.deepcopy(),
                        rendered_panel=rendered_panel,
                        render_panel_method=functools.partial(_render_panel, ui_type=ui_type),
                        render_output_method=functools.partial(_render_output, ui_type=ui_type),
                        reactive_kwargs=solara.reactive(kwargs),
                    )
                    reacton.display(element, mime_bundle=mime_bundle)

                else:
                    import IPython.display
                    IPython.display.display(mime_bundle, raw=True)
            case _:
                rendered_panel = _render_panel(ui_type, *args, **kwargs)
                output = _render_output(rendered_panel, ui_type)
                if return_output_if_str:
                    return output
                else:
                    print(output)

    def _peek_models(
        self,
        models: dict[str, 'Model'],
        title: str = '',
        frame: Frame | None = None,
        **kwargs,
    ) -> DraftPanel:
        from omnipy.data.dataset import Dataset

        ui_type = self._extract_ui_type(**kwargs)
        if not frame:
            frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._create_output_config_from_data_config(ui_type, use_min_crop_width=True)
        config_kwargs = self._validate_kwargs_for_config(**kwargs)
        config = self._apply_validated_kwargs_to_config(config, **config_kwargs)
        layout: Layout[DraftPanel] = Layout()

        frame = self._apply_kwargs_to_frame(frame, **kwargs)
        max_num_panels: None | int = self._calc_max_num_panels(config, frame)

        for i, (inner_title, model) in enumerate(models.items()):
            if max_num_panels is not None and i > max_num_panels:
                # If the number of models exceeds the maximum number of
                # models that can possibly fit in the frame based on the
                # `min_width` config, we stop adding more models.
                print(i)
                break

            if isinstance(model.content, Dataset):
                inner_kwargs = config_kwargs.copy()
                if 'freedom' not in inner_kwargs:
                    inner_kwargs['freedom'] = None

                layout[inner_title] = cast(Dataset, model.content)._peek_dataset_models(
                    title=inner_title,
                    frame=empty_frame(),
                    **inner_kwargs,
                )
            else:
                layout[inner_title] = self._create_inner_panel_for_model(
                    config, model, model.outer_type(), inner_title, **config_kwargs)

        config = self._update_config_with_overflow_modes(config, 'layout')
        config = self._apply_validated_kwargs_to_config(config, **config_kwargs)

        return DraftPanel(layout, title=title, frame=frame, config=config)

    def _calc_max_num_panels(self, config: OutputConfig, frame: Frame) -> int | None:
        max_num_panels: None | int = None
        if has_width(frame.dims):
            panel_design_dims = PanelDesignDims.create(config.panel)
            max_num_panels = panel_design_dims.num_panels_within_frame_width(
                frame.dims.width,
                config.min_panel_width,
            )
        return max_num_panels

    def _apply_kwargs_to_frame(
        self,
        frame: Frame,
        **kwargs,
    ) -> Frame:

        self._check_kwarg_keys(**kwargs)
        frame_kwargs = {k: v for k, v in kwargs.items() if k in _DimsRestatedParams.__annotations__}
        if frame_kwargs:
            frame = frame.modified_copy(**frame_kwargs)

        return frame

    def _validate_kwargs_for_config(
        self,
        **kwargs,
    ) -> dict[str, Any]:
        self._check_kwarg_keys(**kwargs)
        config_kwargs = {k: v for k, v in kwargs.items() if k in OutputConfig.__annotations__}

        config_kwargs = self._update_config_kwargs_with_show_style_in_panel_if_random_style(
            **config_kwargs)

        return {
            k: v
            for k, v in (dataclasses.asdict(OutputConfig(**config_kwargs))).items()
            if k in config_kwargs
        }

    def _apply_validated_kwargs_to_config(
        self,
        config: OutputConfig,
        **config_kwargs,
    ) -> OutputConfig:

        if config_kwargs:
            config = dataclasses.replace(config, **config_kwargs)

        return config

    def _update_config_kwargs_with_show_style_in_panel_if_random_style(
        self,
        **config_kwargs,
    ):
        if 'style' in config_kwargs:
            if 'panel' in config_kwargs:
                panel_design: PanelDesign.Literals = config_kwargs['panel']
            else:
                panel_design = OutputConfig().panel  # Default value

            color_style: AllColorStyles.Literals | str = config_kwargs['style']
            panel_design = self._show_style_in_panel_if_random_style(panel_design, color_style)

            config_kwargs['panel'] = panel_design

        return config_kwargs

    def _check_kwarg_keys(self, **kwargs):
        supported_keys = (
            list(_DimsRestatedParams.__annotations__.keys())
            + list(OutputConfig.__annotations__.keys()))
        extra_keys = (kwargs.keys() - set(supported_keys))

        if extra_keys:
            raise TypeError(f"Unexpected keyword arguments: {', '.join(extra_keys)}. "
                            f'Expected only Dimensions and OutputConfig parameters: '
                            f"{', '.join(supported_keys)}.")

    def _browse_models(self,
                       models: dict[str, 'Model'],
                       initial_html_output: dict[str, str] | None = None,
                       **kwargs) -> None:
        from omnipy.data.dataset import Dataset

        ui_type = self._extract_ui_type(**kwargs)

        html_output = initial_html_output or {}
        all_urls = []

        for name, model in models.items():
            if isinstance(model.content, Dataset):
                cast(Dataset, model.content)._browse_dataset(html_output, **kwargs)
            else:
                filename = f'{name}_{id(model)}.html'
                html_output[filename] = model._display_according_to_ui_type(
                    ui_type=UserInterfaceType.BROWSER_PAGE,
                    return_output_if_str=True,
                    output_method=model._browse_model,
                    **kwargs,
                )

        if ui_type is UserInterfaceType.JUPYTER:
            from omnipy.data._display.integrations.jupyter.components import ModelBrowser
            ModelBrowser(html_content=html_output)._ipython_display_()
        else:
            for filename, html_content in html_output.items():
                file_path = self._create_cached_html_file(filename, html_content)
                all_urls.append(file_path.as_uri())

            browser = webbrowser.get()
            if isinstance(browser, OmnipyMacOSXOSAScript):
                webbrowser.open_new(all_urls)  # type: ignore[arg-type]
            else:
                # For other browsers, we open each URL in a new tab
                for i, url in enumerate(all_urls):
                    webbrowser.open(url, new=(i == 0))

    def _create_cached_html_file(self, filename: str, html_output: str) -> Path:
        self_as_dataclass = cast(DataClassBase, self)

        # TODO: Improve file caching mechanism, including style files
        cache_dir_path = Path(self_as_dataclass.config.ui.cache_dir_path)
        if not cache_dir_path:
            os.makedirs(cache_dir_path)

        file_path = cache_dir_path / sanitize_filename(filename)

        with open(file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_output)

        return file_path

    def _create_inner_panel_for_model(
        self,
        config: OutputConfig,
        model: 'Model',
        outer_type: TypeForm,
        title: str = '',
        frame: Frame | None = None,
        **config_kwargs,
    ) -> DraftPanel:
        from omnipy.components.json.models import is_json_model_instance_hack
        from omnipy.components.raw.models import BytesModel, StrModel

        syntax: SyntaxLanguage.Literals
        if outer_type is str or isinstance(model, StrModel):
            syntax = SyntaxLanguage.TEXT
        if outer_type is bytes or isinstance(model, BytesModel):
            syntax = SyntaxLanguage.HEXDUMP
        elif is_json_model_instance_hack(model):
            syntax = SyntaxLanguage.JSON
        else:
            syntax = SyntaxLanguage.PYTHON

        config = self._update_config_with_overflow_modes(config, 'text')
        config = dataclasses.replace(config, syntax=syntax)
        config = self._apply_validated_kwargs_to_config(config, **config_kwargs)
        return DraftPanel(
            model,
            title=title,
            frame=frame,
            config=config,
        )

    def _update_config_with_overflow_modes(
        self,
        config: OutputConfig,
        panel_type: Literal['text', 'layout'],
    ) -> OutputConfig:
        ui_config = cast(DataClassBase, self).config.ui
        overflow_config = getattr(ui_config, panel_type).overflow

        config = dataclasses.replace(
            config,
            h_overflow=overflow_config.horizontal,
            v_overflow=overflow_config.vertical,
        )
        return config

    @staticmethod
    @functools.lru_cache
    def _get_output_according_to_ui_type(
        stylized_panel: FullyRenderedPanel,
        ui_type: SpecifiedUserInterfaceType.Literals,
    ) -> str:  # pyright: ignore [reportReturnType]
        match ui_type:
            case x if UserInterfaceType.requires_terminal_output(x):
                return stylized_panel.colorized.terminal
            case x if UserInterfaceType.requires_html_tag_output(x):
                return stylized_panel.colorized.html_tag
            case x if UserInterfaceType.requires_html_page_output(x):
                return stylized_panel.colorized.html_page

    def _create_output_config_from_data_config(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
        use_min_crop_width: bool = False,
    ) -> OutputConfig:
        ui_config = cast(DataClassBase, self).config.ui
        ui_type_config = ui_config.get_ui_type_config(ui_type)

        color_system = self._get_color_system_for_user_interface(ui_type, ui_type_config)

        panel_design = ui_config.layout.panel_design
        color_style = ui_type_config.color.style
        panel_design = self._show_style_in_panel_if_random_style(panel_design, color_style)

        config = OutputConfig(
            tab=ui_config.text.tab_size,
            indent=ui_config.text.indent_tab_size,
            printer=ui_config.text.pretty_printer,
            freedom=ui_config.text.proportional_freedom,
            debug=ui_config.text.debug_mode,
            ui=ui_type,
            system=color_system,
            style=color_style,
            bg=ui_type_config.color.solid_background,
            panel=panel_design,
            title_at_top=ui_config.layout.panel_title_at_top,
            max_title_height=ui_config.layout.max_title_height,
            min_panel_width=ui_config.layout.min_panel_width,
            min_crop_width=ui_config.layout.min_crop_width,
            use_min_crop_width=use_min_crop_width,
            justify=ui_config.layout.justify,
        )

        if isinstance(ui_type_config, IsHtmlUserInterfaceConfig):
            config = dataclasses.replace(
                config,
                fonts=ui_type_config.font.families,
                font_size=ui_type_config.font.size,
                font_weight=ui_type_config.font.weight,
                line_height=ui_type_config.font.line_height,
            )
        return config

    def _show_style_in_panel_if_random_style(
        self,
        panel_design: PanelDesign.Literals,
        color_style: AllColorStyles.Literals | str,
    ) -> PanelDesign.Literals:

        if AllColorStyles.is_random_choice_value(color_style):
            if panel_design is PanelDesign.TABLE:
                panel_design = PanelDesign.TABLE_SHOW_STYLE

        return panel_design

    def _get_color_system_for_user_interface(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
        ui_type_config: IsUserInterfaceTypeConfig,
    ) -> DisplayColorSystem.Literals:

        color_system: DisplayColorSystem.Literals

        match ui_type:
            case x if UserInterfaceType.supports_rgb_color_output(x):
                color_system = DisplayColorSystem.ANSI_RGB
            case _:
                color_system = ui_type_config.color.system

        return color_system

    def _define_frame_from_available_display_dims(
            self, ui_type: SpecifiedUserInterfaceType.Literals) -> Frame:
        ui_config = cast(DataClassBase, self).config.ui
        ui_type_config: IsUserInterfaceTypeConfig = ui_config.get_ui_type_config(ui_type)

        width = ui_type_config.width
        height = ui_type_config.height

        if UserInterfaceType.requires_terminal_output(ui_type) and height is not None:
            # Reserve space for the command line prompt
            height -= get_terminal_prompt_height(ui_type)

        return Frame(
            Dimensions(
                width=width,
                height=height,
            ),
            fixed_width=False,
            fixed_height=False,
        )


class ModelDisplayMixin(BaseDisplayMixin):
    def _default_panel(self, **kwargs) -> DraftPanel:
        return self._peek(**kwargs)

    def _peek(self, **kwargs) -> DraftPanel:
        self_as_model = cast('Model', self)
        return self._peek_models(models={self.__class__.__name__: self_as_model}, **kwargs)

    def _full(self, **kwargs) -> DraftPanel:
        return self._peek(**self._prepare_kwargs_for_full(kwargs))

    def _browse(self, **kwargs) -> None:
        self_as_model = cast('Model', self)
        self._browse_models(models={self_as_model.__class__.__name__: self_as_model}, **kwargs)

    def _browse_model(self, **kwargs) -> DraftPanel:
        self_as_model = cast('Model', self)
        ui_type = UserInterfaceType.BROWSER_PAGE

        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._create_output_config_from_data_config(ui_type, use_min_crop_width=False)

        frame = self._apply_kwargs_to_frame(frame, **kwargs)

        config_kwargs = self._validate_kwargs_for_config(**kwargs)
        config = self._apply_validated_kwargs_to_config(config, **config_kwargs)

        return self._create_inner_panel_for_model(
            config,
            self_as_model,
            self_as_model.outer_type(),
            frame=frame,
            **config_kwargs,
        )


class DatasetDisplayMixin(BaseDisplayMixin):
    def _default_panel(self, **kwargs) -> DraftPanel:
        return self._list(**kwargs)

    def _peek(self, **kwargs) -> DraftPanel:
        return self._peek_dataset_models(**kwargs)

    def _peek_dataset_models(self,
                             title: str = '',
                             frame: Frame | None = None,
                             **kwargs) -> DraftPanel:
        self_as_dataset = cast('Dataset', self)
        return self._peek_models(
            models={
                f'{i}. {inner_title}': model
                for i, (inner_title, model) in enumerate(self_as_dataset.data.items())
            },
            title=title,
            frame=frame,
            **kwargs)

    def _full(self, **kwargs) -> DraftPanel:
        return self._list(**self._prepare_kwargs_for_full(kwargs))

    @takes_input_params_from(_DisplayMethodParams.__init__)
    def list(self, **kwargs) -> 'Element | None':
        """
        Displays a list of all models in the dataset, including their
        data file names, types, lengths, and sizes in memory. The output
        is automatically limited by the available display dimensions.

        :return: If the UI type is Jupyter running in browser, `list`
        returns a ReactivelyResizingHtml element which is a Jupyter widget
        to display HTML output in the browser. Otherwise, returns None.
        """
        return self._display_according_to_ui_type(
            ui_type=self._extract_ui_type(**kwargs),
            return_output_if_str=False,
            output_method=self._list,
            **kwargs,
        )

    def _list(self, **kwargs) -> DraftPanel:
        dataset = cast('Dataset', self)

        ui_type = self._extract_ui_type(**kwargs)
        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._create_output_config_from_data_config(ui_type, use_min_crop_width=False)
        config = self._update_config_with_overflow_modes(config, 'layout')

        config = dataclasses.replace(config, max_title_height=MaxTitleHeight.ONE)
        right_justified_config = dataclasses.replace(config, justify='right')
        text_config = dataclasses.replace(config, syntax=SyntaxLanguage.TEXT)

        frame = self._apply_kwargs_to_frame(frame, **kwargs)
        config_kwargs = self._validate_kwargs_for_config(**kwargs)
        config = self._apply_validated_kwargs_to_config(config, **config_kwargs)
        right_justified_config = self._apply_validated_kwargs_to_config(
            right_justified_config, **config_kwargs)
        text_config = self._apply_validated_kwargs_to_config(text_config, **config_kwargs)

        # TODO: Add dataset title for dataset peek()
        # _title = self.__class__.__name__

        layout: Layout[DraftPanel] = Layout()

        max_digits_for_dataset_list_index_numbers = self._max_digits_for_dataset_list_index_numbers(
            dataset,
            frame,
            config,
        )

        layout['#'] = DraftPanel(
            '\n'.join(str(i) for i in range(len(dataset))),
            title='#',
            frame=Frame(
                Dimensions(max_digits_for_dataset_list_index_numbers, None), fixed_width=True),
            config=config)
        layout['Data file name'] = DraftPanel(
            '\n'.join(dataset.data.keys()), title='Data file name', config=text_config)
        layout['Type'] = DraftPanel(
            '\n'.join(self._type_str(v) for v in dataset.data.values()),
            title='Type',
            config=config)
        layout['Length'] = DraftPanel(
            '\n'.join(str(self._len_if_available(v)) for v in dataset.data.values()),
            title='Length',
            config=right_justified_config)
        layout['Size (in memory)'] = DraftPanel(
            '\n'.join(self._obj_size_if_available(v) for v in dataset.data.values()),
            title='Size (in memory)',
            config=right_justified_config)

        return DraftPanel(layout, frame=frame, config=config)

    def _max_digits_for_dataset_list_index_numbers(
        self,
        dataset: 'Dataset',
        frame: Frame,
        config: OutputConfig,
    ) -> int:
        panels_design_dims = PanelDesignDims.create(config.panel)

        if has_height(frame.dims):
            inner_frame_height = (
                frame.dims.height - panels_design_dims.num_extra_vertical_chars(1)
                - config.max_title_height - TITLE_BLANK_LINES)
            num_panels_listed_in_view = min(len(dataset), inner_frame_height)
        else:
            num_panels_listed_in_view = len(dataset)

        # -1 is due to indices starting at 0
        max_digits_for_dataset_list_index_numbers = len(str(num_panels_listed_in_view - 1))

        return max_digits_for_dataset_list_index_numbers

    def _browse(self, **kwargs) -> None:
        self._browse_dataset(**kwargs)

    def _browse_dataset(self, html_output: dict[str, str] | None = None, **kwargs) -> None:
        self_as_dataset = cast('Dataset', self)
        if html_output is None:
            html_output = {}

        self_as_dataset = cast('Dataset', self)

        filename = f'{self.__class__.__name__}_{id(self)}.html'

        kwargs_copy = kwargs.copy()
        kwargs_copy['ui'] = UserInterfaceType.BROWSER_PAGE

        html_output[filename] = self._display_according_to_ui_type(
            ui_type=UserInterfaceType.BROWSER_PAGE,
            return_output_if_str=True,
            output_method=self._list,
            **kwargs_copy,
        )

        self._browse_models(
            models={
                f'{i}. {title}': model
                for i, (title, model) in enumerate(self_as_dataset.data.items())
            },
            initial_html_output=html_output,
            **kwargs)

    @classmethod
    def _type_str(cls, obj: Any) -> str:
        if isinstance(obj, PendingData):
            return f'{obj.job_name} -> Data pending...'
        elif isinstance(obj, FailedData):
            return f'{obj.job_name} -> {obj.exception.__class__.__name__}: {obj.exception}'
        else:
            return type(obj).__name__

    @classmethod
    def _len_if_available(cls, obj: Any) -> int | str:
        try:
            return len(obj)
        except TypeError:
            return '-'

    @classmethod
    def _obj_size_if_available(cls, obj: Any) -> str:
        if isinstance(obj, PendingData):
            return '-'
        else:
            try:
                cached_obj_size_func = functools.cache(cls._obj_size)
                return cached_obj_size_func(obj)
            except TypeError:
                return cls._obj_size(obj)

    @staticmethod
    def _obj_size(obj: Any) -> str:
        import humanize
        import objsize

        return humanize.naturalsize(objsize.get_deep_size(obj))
