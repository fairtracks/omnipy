from abc import ABCMeta, abstractmethod
import dataclasses
import functools
import inspect
from typing import Any, cast, Literal, TYPE_CHECKING

from typing_extensions import assert_never

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
from omnipy.shared.enums.ui import SpecifiedUserInterfaceType, UserInterfaceType
from omnipy.shared.protocols.config import (IsHtmlUserInterfaceConfig,
                                            IsUserInterfaceConfig,
                                            IsUserInterfaceTypeConfig)
import omnipy.util._pydantic as pyd

if TYPE_CHECKING:
    from reacton.core import Element

    from omnipy.data.model import Model


class BaseDisplayMixin(metaclass=ABCMeta):
    @abstractmethod
    def _display(self) -> 'str | Element':
        ...

    def peek(self) -> 'str | Element':
        return self._insert_any_reactive_components('_peek')

    @abstractmethod
    def _peek(self) -> 'str | Element':
        ...

    def __str__(self) -> str:
        return repr(self)

    def _repr_pretty_(self, p, cycle: bool) -> None:
        if cycle:
            p.text(f'{cast(pyd.GenericModel, self).__repr_name__()}(...)')
        else:
            if len(p.stack) == 1:
                ui_type = self._determine_ui_type(UserInterfaceType.AUTO)
                if UserInterfaceType.is_jupyter(ui_type):
                    p.text(self._default_repr())
            else:
                p.text(self.__repr__())

    def _repr_html_(self) -> str:
        from reacton.core import Element
        element = cast(Element, self._display())
        element._ipython_display_()
        return ''

    @staticmethod
    @functools.lru_cache
    def _determine_ui_type(ui_type: UserInterfaceType.Literals) -> UserInterfaceType.Literals:
        if ui_type is UserInterfaceType.AUTO:
            ui_type = detect_ui_type()
        return ui_type

    def _insert_any_reactive_components(
        self,
        method_name: str,
        **kwargs: Any,
    ) -> 'str | Element':
        ui_type: UserInterfaceType.Literals = UserInterfaceType.AUTO
        from omnipy.data.dataset import Dataset, Model

        ui_type = self._determine_ui_type(ui_type)

        if ui_type is UserInterfaceType.JUPYTER:
            from omnipy.data._display.jupyter.components import DynamiclyResizingHtml
            return DynamiclyResizingHtml(
                cast(Dataset | Model, self),
                method_name=method_name,
                **kwargs,
            )
        else:
            return getattr(self, method_name)(**kwargs)

    def _peek_models(
        self,
        models: dict[str, 'Model'],
    ) -> 'str | Element':
        ui_type: UserInterfaceType.Literals = UserInterfaceType.AUTO,
        from omnipy.data.dataset import Dataset

        ui_type = self._determine_ui_type(ui_type)
        frame = self._define_frame_from_available_display_dims(ui_type)
        config = self._get_output_config(ui_type)
        layout: Layout[DraftPanel] = Layout()

        for title, model in models.items():
            outer_type = model.outer_type()
            if inspect.isclass(outer_type) and issubclass(outer_type, Dataset):
                return cast(Dataset, model.contents).peek()

            layout[title] = self._create_inner_panel_for_model(config, model, outer_type, title)

        config = self._set_overflow_modes_and_other_configs(config, 'layout')
        panel = DraftPanel(layout, frame=frame, config=config)
        resized_panel = panel.render_next_stage()
        stylized_panel = resized_panel.render_next_stage()
        return self._get_output_according_to_ui_type(stylized_panel, ui_type)

    def _create_inner_panel_for_model(self, config, model, outer_type, title):
        from omnipy.components.json.models import JsonModel
        from omnipy.components.raw.models import StrModel

        if outer_type is str or isinstance(model, StrModel):
            language = SyntaxLanguage.TEXT
        elif isinstance(model, JsonModel):
            language = SyntaxLanguage.JSON
        else:
            language = SyntaxLanguage.PYTHON

        config = self._set_overflow_modes_and_other_configs(config, 'text', language=language)

        match language:
            case SyntaxLanguage.TEXT:
                return TextDraftPanel(cast(str, model.contents), title=title, config=config)
            case SyntaxLanguage.JSON:
                return TextDraftPanel(model.to_json(), title=title, config=config)
            case _:  # SyntaxLanguage.PYTHON
                return DraftPanel(model, title=title, config=config)

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

    @staticmethod
    def _get_ui_type_config(
        ui_config: IsUserInterfaceConfig,
        ui_type: SpecifiedUserInterfaceType.Literals,
    ) -> IsUserInterfaceTypeConfig:
        match ui_type:
            case x if UserInterfaceType.is_terminal(x):
                ui_config_attr = 'terminal'
            case x if UserInterfaceType.is_jupyter(x):
                ui_config_attr = 'jupyter'
            case x if UserInterfaceType.is_browser(x):
                ui_config_attr = 'browser'
            case _ as never:
                raise assert_never(never)  # pyright: ignore [reportArgumentType]
        return getattr(ui_config, ui_config_attr)

    def _get_output_config(self, ui_type: SpecifiedUserInterfaceType.Literals) -> OutputConfig:
        ui_config = cast(DataClassBase, self).config.ui
        ui_type_config: IsUserInterfaceTypeConfig = self._get_ui_type_config(ui_config, ui_type)

        match ui_type:
            case UserInterfaceType.UNKNOWN:
                color_system = DisplayColorSystem.AUTO
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

    def _define_frame_from_available_display_dims(self,
                                                  ui_type: UserInterfaceType.Literals) -> Frame:
        ui_config = cast(DataClassBase, self).config.ui
        ui_type_config: IsUserInterfaceTypeConfig = self._get_ui_type_config(ui_config, ui_type)

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
    def _display(self) -> 'str | Element':
        return self.peek()

    def _peek(self) -> 'str | Element':
        from omnipy.data.model import Model
        return self._peek_models(models={self.__class__.__name__: cast(Model, self)})


class DatasetDisplayMixin(BaseDisplayMixin):
    def _display(self) -> 'str | Element':
        return self.list()

    def _peek(self) -> 'str | Element':
        from omnipy.data.dataset import Dataset
        self_as_dataset = cast(Dataset, self)
        return self._peek_models({
            f'{i}. {title}': model for i, (title, model) in enumerate(self_as_dataset.data.items())
        })

    def list(self) -> 'str | Element':
        return self._insert_any_reactive_components('_list')

    def _list(self) -> str:
        from omnipy.data.dataset import Dataset
        dataset = cast(Dataset, self)

        ui_type = self._determine_ui_type(UserInterfaceType.AUTO)
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

        panel = DraftPanel(layout, frame=frame, config=config)

        resized_panel = panel.render_next_stage()
        stylized_panel = resized_panel.render_next_stage()
        return self._get_output_according_to_ui_type(stylized_panel, ui_type)

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
