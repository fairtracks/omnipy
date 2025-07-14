from abc import ABCMeta, abstractmethod
import dataclasses
import functools
import inspect
from typing import Any, cast, Literal, overload, ParamSpec, TYPE_CHECKING

from typing_extensions import assert_never, LiteralString, TypeVar

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.base import FullyRenderedPanel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import TextDraftPanel
from omnipy.data.helpers import FailedData, PendingData
from omnipy.hub.ui import detect_ui_type, get_terminal_prompt_height
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

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter
    from reacton.core import Element

    from omnipy.data.model import Model

P = ParamSpec('P')
LiteralT = TypeVar('LiteralT', bound=LiteralString)


class BaseDisplayMixin(metaclass=ABCMeta):
    @abstractmethod
    def _default_panel(self) -> DraftPanel:
        ...

    def default_repr_to_terminal_str(self,
                                     ui_type: TerminalOutputUserInterfaceType.Literals) -> str:
        return self._display_according_to_ui_type(
            ui_type=ui_type,
            return_output_if_str=True,
            output_method=self._default_panel,
        )

    def peek(self) -> 'Element | None':
        return self._display_according_to_ui_type(
            ui_type=self._detect_ui_type_if_auto(UserInterfaceType.AUTO),
            return_output_if_str=False,
            output_method=self._peek,
        )

    @abstractmethod
    def _peek(self) -> DraftPanel:
        ...

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
                ui_type = self._detect_ui_type_if_auto(UserInterfaceType.AUTO)
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
        ui_type = self._detect_ui_type_if_auto(UserInterfaceType.AUTO)
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

    @staticmethod
    @functools.lru_cache
    def _detect_ui_type_if_auto(
            ui_type: UserInterfaceType.Literals) -> SpecifiedUserInterfaceType.Literals:
        if ui_type == UserInterfaceType.AUTO:
            return detect_ui_type()
        else:
            return ui_type

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
                from omnipy.data._display.jupyter.components import ReactivelyResizingHtml
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

    def _peek_models(
        self,
        models: dict[str, 'Model'],
    ) -> DraftPanel:
        from omnipy.data.dataset import Dataset

        ui_type = self._detect_ui_type_if_auto(UserInterfaceType.AUTO)
        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._get_output_config(ui_type)
        layout: Layout[DraftPanel] = Layout()

        for title, model in models.items():
            outer_type = model.outer_type()
            if inspect.isclass(outer_type) and issubclass(outer_type, Dataset):
                return cast(Dataset, model.contents)._peek()

            layout[title] = self._create_inner_panel_for_model(config, model, outer_type, title)

        config = self._set_overflow_modes_and_other_configs(config, 'layout')
        return DraftPanel(layout, frame=frame, config=config)

    def _create_inner_panel_for_model(
        self,
        config: OutputConfig,
        model: 'Model',
        outer_type: TypeForm,
        title: str = '',
        frame: Frame | None = None,
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

        config = self._set_overflow_modes_and_other_configs(config, 'text', language=language)

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

    def _set_overflow_modes_and_other_configs(
        self,
        config: OutputConfig,
        panel_type: Literal['text', 'layout'],
        **kwargs: Any,
    ) -> OutputConfig:
        ui_config = cast(DataClassBase, self).config.ui
        overflow_config = getattr(ui_config, panel_type).overflow

        config = dataclasses.replace(
            config,
            horizontal_overflow_mode=overflow_config.horizontal,
            vertical_overflow_mode=overflow_config.vertical,
            **kwargs,
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

    def _get_output_config(self, ui_type: SpecifiedUserInterfaceType.Literals) -> OutputConfig:
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
            debug_mode=ui_config.text.debug_mode,
            pretty_printer=ui_config.text.pretty_printer,
            color_system=color_system,
            color_style=ui_type_config.color.style,
            transparent_background=ui_type_config.color.transparent_background,
            panel_design=ui_config.layout.panel_design,
            panel_title_at_top=ui_config.layout.panel_title_at_top,
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

    def _peek(self) -> DraftPanel:
        from omnipy.data.model import Model
        return self._peek_models(models={self.__class__.__name__: cast(Model, self)})


class DatasetDisplayMixin(BaseDisplayMixin):
    def _default_panel(self) -> DraftPanel:
        return self._list()

    def _peek(self) -> DraftPanel:
        from omnipy.data.dataset import Dataset
        self_as_dataset = cast(Dataset, self)
        return self._peek_models({
            f'{i}. {title}': model for i, (title, model) in enumerate(self_as_dataset.data.items())
        })

    def list(self) -> 'Element | None':
        return self._display_according_to_ui_type(
            ui_type=self._detect_ui_type_if_auto(UserInterfaceType.AUTO),
            return_output_if_str=False,
            output_method=self._list,
        )

    def _list(self) -> DraftPanel:
        from omnipy.data.dataset import Dataset
        dataset = cast(Dataset, self)

        ui_type = self._detect_ui_type_if_auto(UserInterfaceType.AUTO)
        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._get_output_config(ui_type)

        config = self._set_overflow_modes_and_other_configs(
            config,
            'layout',
            max_title_height=MaxTitleHeight.ONE,
        )
        right_justified_config = dataclasses.replace(config, justify_in_layout='right')
        text_config = dataclasses.replace(config, language=SyntaxLanguage.TEXT)

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
            config=text_config)
        layout['Length'] = TextDraftPanel(
            '\n'.join(str(self._len_if_available(v)) for v in dataset.data.values()),
            title='Length',
            config=right_justified_config)
        layout['Size (in memory)'] = TextDraftPanel(
            '\n'.join(self._obj_size_if_available(v) for v in dataset.data.values()),
            title='Size (in memory)',
            config=right_justified_config)

        return DraftPanel(layout, frame=frame, config=config)

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
