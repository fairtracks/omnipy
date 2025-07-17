from abc import ABCMeta, abstractmethod
import dataclasses
import functools
import inspect
from pathlib import Path
import sys
from typing import Any, cast, Literal, overload, ParamSpec, TYPE_CHECKING
import webbrowser

from typing_extensions import assert_never, LiteralString, TypeVar

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.integrations.browser.macosx import (OmnipyMacOSXOSAScript,
                                                              setup_macosx_browser_integration)
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.base import FullyRenderedPanel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import TextDraftPanel
from omnipy.data.helpers import FailedData, PendingData
from omnipy.hub.ui import get_terminal_prompt_height
from omnipy.shared.enums.colorstyles import RecommendedColorStyles
from omnipy.shared.enums.display import DisplayColorSystem, MaxTitleHeight, SyntaxLanguage
from omnipy.shared.enums.ui import (BrowserPageUserInterfaceType,
                                    BrowserUserInterfaceType,
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
    def _default_panel(self) -> DraftPanel:
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
        preview of the model's contents, and for datasets, this is a
        side-by-side view of each model contained in the dataset. Both views
        are automatically limited by the available display dimensions.
        :return: If the UI type is Jupyter runnint in in browser, `peek`
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
        return (kwargs.get('user_interface_type', None)
                or cast(DataClassBase, self).config.ui.detected_type)

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
        kwargs_copy = kwargs.copy()
        kwargs_copy['height'] = None

        return self._display_according_to_ui_type(
            ui_type=self._extract_ui_type(**kwargs),
            return_output_if_str=False,
            output_method=self._full,
            **kwargs_copy)

    @takes_input_params_from(_DisplayMethodParams.__init__)
    def browse(self, **kwargs) -> None:
        """
        Opens the model or dataset in a browser, if possible. For models,
        this is a detailed view of the model's contents, and for datasets
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
    def _docs(self, **kwargs) -> None:
        """
        Displays a preview of the model or dataset for the documentation.
        """
        self.peek(
            user_interface_type=SpecifiedUserInterfaceType.BROWSER_TAG,
            color_style=RecommendedColorStyles.OMNIPY_SELENIZED_WHITE,
            **kwargs)

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

    def _repr_html_(self) -> str:
        ui_type = cast(DataClassBase, self).config.ui.detected_type
        if UserInterfaceType.is_jupyter_in_browser(ui_type):
            from reacton.core import Element
            element: Element = self._display_according_to_ui_type(
                ui_type=ui_type,
                return_output_if_str=False,
                output_method=self._default_panel,
            )
            element._ipython_display_()
        elif UserInterfaceType.is_jupyter_embedded(ui_type):
            print(self.default_repr_to_terminal_str(ui_type))
        return ''

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
    ) -> 'Element':
        ...

    def _display_according_to_ui_type(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
        return_output_if_str: bool,
        output_method: Method[P, DraftPanel],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> 'str | Element | None':
        from omnipy.data.dataset import Dataset, Model

        def _render_output(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> str:
            panel = output_method(*args, **kwargs)
            resized_panel = panel.render_next_stage()
            if ui_type in BrowserPageUserInterfaceType:
                # If the output is a browser page, we allow expanding the frame to fit the contents
                if not resized_panel.within_frame.width:
                    wider_panel = dataclasses.replace(
                        panel,
                        frame=panel.frame.modified_copy(width=resized_panel.dims.width),
                    )
                    resized_panel = wider_panel.render_next_stage()
            stylized_panel = resized_panel.render_next_stage()

            match ui_type:
                case x if UserInterfaceType.requires_terminal_output(x):
                    return stylized_panel.colorized.terminal
                case x if UserInterfaceType.requires_html_tag_output(x):
                    return stylized_panel.colorized.html_tag
                case x if UserInterfaceType.requires_html_page_output(x):
                    return stylized_panel.colorized.html_page
                case _ as never:
                    # Only supported by mypy, see https://github.com/microsoft/pyright/issues/10680
                    assert_never(never)  # pyright: ignore [reportArgumentType]

        match ui_type:
            case x if UserInterfaceType.is_jupyter_in_browser(x):
                from omnipy.data._display.integrations.jupyter.components import \
                    ReactivelyResizingHtml
                element: Element = ReactivelyResizingHtml(
                    cast(Dataset | Model, self),
                    output_method=_render_output,
                    *args,
                    **kwargs,
                )
                return element
            case _:
                output = _render_output(*args, **kwargs)
                if return_output_if_str:
                    return output
                else:
                    print(output)

    def _peek_models(self, models: dict[str, 'Model'], **kwargs) -> DraftPanel:
        from omnipy.data.dataset import Dataset

        ui_type = cast(DataClassBase, self).config.ui.detected_type
        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._extract_output_config_from_data_config(ui_type)
        layout: Layout[DraftPanel] = Layout()

        frame = self._apply_kwargs_to_frame(frame, **kwargs)

        for title, model in models.items():
            outer_type = model.outer_type()
            if inspect.isclass(outer_type) and issubclass(outer_type, Dataset):
                return cast(Dataset, model.contents)._peek()

            layout[title] = self._create_inner_panel_for_model(config,
                                                               model,
                                                               outer_type,
                                                               title,
                                                               **kwargs)

        config = self._update_config_with_overflow_modes(config, 'layout')
        config = self._apply_kwargs_to_config(config, **kwargs)

        return DraftPanel(layout, frame=frame, config=config)

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

    def _apply_kwargs_to_config(
        self,
        config: OutputConfig,
        **kwargs,
    ) -> OutputConfig:

        self._check_kwarg_keys(**kwargs)
        config_kwargs = {k: v for k, v in kwargs.items() if k in OutputConfig.__annotations__}
        if config_kwargs:
            config = dataclasses.replace(config, **config_kwargs)

        return config

    def _check_kwarg_keys(self, **kwargs):
        supported_keys = (
            list(_DimsRestatedParams.__annotations__.keys())
            + list(OutputConfig.__annotations__.keys()))
        extra_keys = (kwargs.keys() - set(supported_keys))

        if extra_keys:
            raise TypeError(f"Unexpected keyword arguments: {', '.join(extra_keys)}. "
                            f'Expected only Dimensions and OutputConfig parameters: '
                            f"{', '.join(supported_keys)}.")

    def _browse_models(self, models: dict[str, 'Model'], **kwargs) -> None:
        self_as_dataclass = cast(DataClassBase, self)

        html_output = {}
        all_urls = []
        for name, model in models.items():
            filename = f'{name}_{id(self)}.html'
            html_output[filename] = model._display_according_to_ui_type(
                ui_type=UserInterfaceType.BROWSER_PAGE,
                return_output_if_str=True,
                output_method=model._browse_model,
                **kwargs,
            )

        if self_as_dataclass.config.ui.detected_type is UserInterfaceType.JUPYTER:
            from omnipy.data._display.integrations.jupyter.components import BrowseModels
            BrowseModels(html_contents=html_output)._ipython_display_()
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
        file_path = Path(self_as_dataclass.config.ui.cache_dir_path) / filename

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
        **kwargs,
    ) -> DraftPanel:
        from omnipy.components.json.models import is_json_model_instance_hack
        from omnipy.components.raw.models import StrModel

        language: SyntaxLanguage.Literals
        if outer_type is str or isinstance(model, StrModel):
            language = SyntaxLanguage.TEXT
        elif is_json_model_instance_hack(model):
            language = SyntaxLanguage.JSON
        else:
            language = SyntaxLanguage.PYTHON

        config = self._update_config_with_overflow_modes(config, 'text')
        config = dataclasses.replace(config, language=language)
        config = self._apply_kwargs_to_config(config, **kwargs)

        match language:
            case SyntaxLanguage.TEXT:
                return TextDraftPanel(
                    cast(str, model.contents),
                    title=title,
                    frame=frame,
                    config=config,
                )
            case SyntaxLanguage.PYTHON | SyntaxLanguage.JSON:
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
            horizontal_overflow_mode=overflow_config.horizontal,
            vertical_overflow_mode=overflow_config.vertical,
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

    def _extract_output_config_from_data_config(
        self,
        ui_type: SpecifiedUserInterfaceType.Literals,
    ) -> OutputConfig:
        ui_config = cast(DataClassBase, self).config.ui
        ui_type_config = ui_config.get_ui_type_config(ui_type)

        color_system: DisplayColorSystem.Literals
        match ui_type:
            case x if UserInterfaceType.supports_rgb_color_output(x):
                color_system = DisplayColorSystem.ANSI_RGB
            case _:
                color_system = ui_type_config.color.system

        config = OutputConfig(
            tab_size=ui_config.text.tab_size,
            indent_tab_size=ui_config.text.indent_tab_size,
            pretty_printer=ui_config.text.pretty_printer,
            proportional_freedom=ui_config.text.proportional_freedom,
            debug_mode=ui_config.text.debug_mode,
            user_interface_type=ui_type,
            color_system=color_system,
            color_style=ui_type_config.color.style,
            transparent_background=ui_type_config.color.transparent_background,
            panel_design=ui_config.layout.panel_design,
            panel_title_at_top=ui_config.layout.panel_title_at_top,
            max_title_height=ui_config.layout.max_title_height,
            justify_in_layout=ui_config.layout.justify_in_layout,
        )

        if isinstance(ui_type_config, IsHtmlUserInterfaceConfig):
            config = dataclasses.replace(
                config,
                css_font_families=ui_type_config.font.families,
                css_font_size=ui_type_config.font.size,
                css_font_weight=ui_type_config.font.weight,
                css_line_height=ui_type_config.font.line_height,
            )
        return config

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
    def _default_panel(self) -> DraftPanel:
        return self._peek()

    def _peek(self, **kwargs) -> DraftPanel:
        self_as_model = cast('Model', self)
        return self._peek_models(models={self.__class__.__name__: self_as_model}, **kwargs)

    def _full(self, **kwargs) -> DraftPanel:
        return self._peek(**kwargs)

    def _browse(self, **kwargs) -> None:
        self_as_model = cast('Model', self)
        self._browse_models(models={self_as_model.__class__.__name__: self_as_model}, **kwargs)

    def _browse_model(self, **kwargs) -> DraftPanel:
        self_as_model = cast('Model', self)
        ui_type = UserInterfaceType.BROWSER_PAGE

        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._extract_output_config_from_data_config(ui_type)

        frame = self._apply_kwargs_to_frame(frame, **kwargs)
        config = self._apply_kwargs_to_config(config, **kwargs)

        return self._create_inner_panel_for_model(
            config,
            self_as_model,
            self_as_model.outer_type(),
            frame=frame,
            **kwargs,
        )


class DatasetDisplayMixin(BaseDisplayMixin):
    def _default_panel(self) -> DraftPanel:
        return self._list()

    def _peek(self, **kwargs) -> DraftPanel:
        self_as_dataset = cast('Dataset', self)
        return self._peek_models(
            models={
                f'{i}. {title}': model
                for i, (title, model) in enumerate(self_as_dataset.data.items())
            },
            **kwargs)

    def _full(self, **kwargs) -> DraftPanel:
        return self._list(**kwargs)

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
        from omnipy.data.dataset import Dataset
        dataset = cast(Dataset, self)

        ui_type = cast(DataClassBase, self).config.ui.detected_type
        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._extract_output_config_from_data_config(ui_type)
        config = self._update_config_with_overflow_modes(config, 'layout')

        config = dataclasses.replace(config, max_title_height=MaxTitleHeight.ONE)
        right_justified_config = dataclasses.replace(config, justify_in_layout='right')
        text_config = dataclasses.replace(config, language=SyntaxLanguage.TEXT)

        frame = self._apply_kwargs_to_frame(frame, **kwargs)
        config = self._apply_kwargs_to_config(config, **kwargs)
        right_justified_config = self._apply_kwargs_to_config(right_justified_config, **kwargs)
        text_config = self._apply_kwargs_to_config(text_config, **kwargs)

        # TODO: Add dataset title for dataset peek()
        # _title = self.__class__.__name__

        layout: Layout[TextDraftPanel] = Layout()
        layout['#'] = TextDraftPanel(
            '\n'.join(str(i) for i in range(len(dataset))), title='#', config=config)
        layout['Data file name'] = TextDraftPanel(
            '\n'.join(dataset.data.keys()), title='Data file name', config=text_config)
        layout['Type'] = TextDraftPanel(
            '\n'.join(self._type_str(v) for v in dataset.data.values()),
            title='Type',
            config=config)
        layout['Length'] = TextDraftPanel(
            '\n'.join(str(self._len_if_available(v)) for v in dataset.data.values()),
            title='Length',
            config=right_justified_config)
        layout['Size (in memory)'] = TextDraftPanel(
            '\n'.join(self._obj_size_if_available(v) for v in dataset.data.values()),
            title='Size (in memory)',
            config=right_justified_config)

        return DraftPanel(layout, frame=frame, config=config)

    def _browse(self, **kwargs) -> None:
        self_as_dataset = cast('Dataset', self)

        self._browse_models(
            models={
                f'{i}. {title}': model
                for i, (title, model) in enumerate(self_as_dataset.data.items())
            },
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
