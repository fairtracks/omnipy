from abc import ABCMeta, abstractmethod
import dataclasses
import functools
import inspect
from typing import Any, cast, Literal, TYPE_CHECKING

import humanize
from IPython.lib.pretty import RepresentationPrinter
import objsize

from omnipy.data._data_class_creator import DataClassBase
from omnipy.data._display.config import (OutputConfig,
                                         TERMINAL_DEFAULT_HEIGHT,
                                         TERMINAL_DEFAULT_WIDTH)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.helpers import detect_display_type
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.base import FullyRenderedPanel
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import TextDraftPanel
from omnipy.data.helpers import FailedData, PendingData
from omnipy.shared.enums import ConsoleColorSystem, DisplayType, MaxTitleHeight, SyntaxLanguage
from omnipy.shared.exceptions import ShouldNotOccurException
from omnipy.shared.protocols.config import IsConsoleConfig, IsDisplayConfig, IsHtmlConsoleConfig
import omnipy.util._pydantic as pyd

if TYPE_CHECKING:
    from omnipy.data.model import Model


class BaseDisplayMixin(metaclass=ABCMeta):
    @abstractmethod
    def _display(self) -> str:
        ...

    def peek(self) -> str:
        return self._peek()

    @abstractmethod
    def _peek(self) -> str:
        ...

    def __str__(self) -> str:
        return repr(self)

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        if cycle:
            p.text(f'{cast(pyd.GenericModel, self).__repr_name__()}(...)')
        else:
            if len(p.stack) == 1:
                display_type = self._determine_display_type(DisplayType.AUTO)
                if display_type is not DisplayType.JUPYTER:
                    p.text(self._display())
            else:
                p.text(self.__repr__())


    @staticmethod
    @functools.lru_cache
    def _determine_display_type(display_type: DisplayType,) -> DisplayType:
        if display_type is DisplayType.AUTO:
            display_type = detect_display_type()
        return display_type



    def _peek_models(
        self,
        models: dict[str, 'Model'],
        display_type: DisplayType = DisplayType.AUTO,
    ) -> str:
        from omnipy.data.dataset import Dataset

        display_type = self._determine_display_type(display_type)
        frame = self._define_frame_from_console_size(display_type)
        config = self._get_output_config(display_type)
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
        return self._get_output_according_to_display_type(stylized_panel, display_type)

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
        display_config = cast(DataClassBase, self).config.display
        overflow_config = getattr(display_config, panel_type).overflow

        config = dataclasses.replace(
            config,
            horizontal_overflow_mode=overflow_config.horizontal,
            vertical_overflow_mode=overflow_config.vertical,
            **kwargs,
        )
        return config

    @staticmethod
    @functools.lru_cache
    def _get_output_according_to_display_type(
        stylized_panel: FullyRenderedPanel,
        display_type: DisplayType,
    ) -> str:
        match display_type:
            case (DisplayType.TERMINAL | DisplayType.IPYTHON
                  | DisplayType.PYCHARM_TERMINAL | DisplayType.PYCHARM_IPYTHON
                  | DisplayType.UNKNOWN):
                return stylized_panel.colorized.terminal
            case DisplayType.JUPYTER:
                return stylized_panel.colorized.html_tag
            case DisplayType.BROWSER:
                return stylized_panel.colorized.html_page
            case _:
                raise ValueError(f'Output not supported for display type: {display_type}')

    @staticmethod
    def _get_console_config(
        display_config: IsDisplayConfig,
        display_type: DisplayType,
    ) -> IsConsoleConfig:
        match display_type:
            case (DisplayType.TERMINAL | DisplayType.IPYTHON
                  | DisplayType.PYCHARM_TERMINAL | DisplayType.PYCHARM_IPYTHON
                  | DisplayType.UNKNOWN):
                display_config_attr = 'terminal'
            case DisplayType.JUPYTER:
                display_config_attr = 'jupyter'
            case DisplayType.BROWSER:
                display_config_attr = 'browser'
            case _:
                raise ShouldNotOccurException(f'Incorrect display type: {display_type}')
        return getattr(display_config, display_config_attr)

    def _get_output_config(self, display_type: DisplayType) -> OutputConfig:
        display_config = cast(DataClassBase, self).config.display
        console_config: IsConsoleConfig = self._get_console_config(display_config, display_type)

        match display_type:
            case DisplayType.UNKNOWN:
                color_system = ConsoleColorSystem.AUTO
            case (DisplayType.PYCHARM_TERMINAL | DisplayType.PYCHARM_IPYTHON
                  | DisplayType.JUPYTER | DisplayType.BROWSER):
                color_system = ConsoleColorSystem.ANSI_RGB
            case _:
                color_system = console_config.color.color_system

        config = OutputConfig(
            tab_size=display_config.text.tab_size,
            indent_tab_size=display_config.text.indent_tab_size,
            debug_mode=display_config.text.debug_mode,
            pretty_printer=display_config.text.pretty_printer,
            console_color_system=color_system,
            color_style=console_config.color.color_style,
            transparent_background=console_config.color.transparent_background,
            panel_design=display_config.layout.panel_design,
            panel_title_at_top=display_config.layout.panel_title_at_top,
        )

        if isinstance(console_config, IsHtmlConsoleConfig):
            config = dataclasses.replace(
                config,
                css_font_families=console_config.font.families,
                css_font_size=console_config.font.size,
                css_font_weight=console_config.font.weight,
                css_line_height=console_config.font.line_height,
            )
        return config

    def _define_frame_from_console_size(self, display_type: DisplayType) -> Frame:
        display_config = cast(DataClassBase, self).config.display
        console_config: IsConsoleConfig = self._get_console_config(display_config, display_type)

        width = console_config.width or TERMINAL_DEFAULT_WIDTH
        height = console_config.height or TERMINAL_DEFAULT_HEIGHT


        return Frame(
            Dimensions(
                width=width,
                height=height,
            ),
            fixed_width=False,
            fixed_height=False,
        )


class ModelDisplayMixin(BaseDisplayMixin):
    def _display(self) -> str:
        return self.peek()

    def _peek(self) -> str:
        from omnipy.data.model import Model
        return self._peek_models(models={self.__class__.__name__: cast(Model, self)})


class DatasetDisplayMixin(BaseDisplayMixin):
    def _display(self) -> str:
        return self.list()

    def _peek(self) -> str:
        from omnipy.data.dataset import Dataset
        self_as_dataset = cast(Dataset, self)
        return self._peek_models({
            f'{i}. {title}': model for i, (title, model) in enumerate(self_as_dataset.data.items())
        })

    def list(self) -> str:
        return self._list()

    def _list(self) -> str:
        from omnipy.data.dataset import Dataset
        dataset = cast(Dataset, self)

        display_type = self._determine_display_type(DisplayType.AUTO)
        frame = self._define_frame_from_console_size(display_type)
        config = self._get_output_config(display_type)

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
        return self._get_output_according_to_display_type(stylized_panel, display_type)

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
        return humanize.naturalsize(objsize.get_deep_size(obj))
