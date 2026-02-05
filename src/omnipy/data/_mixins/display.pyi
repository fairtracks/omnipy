import abc
from inspect import signature as signature
from typing import ParamSpec, Protocol

from IPython.lib.pretty import RepresentationPrinter as RepresentationPrinter  # type: ignore
from reacton.core import Element as Element
from typing_extensions import TypedDict, TypeVar, Unpack

from omnipy.data._data_class_creator import DataClassBase as DataClassBase
from omnipy.data._display.config import OutputConfig as OutputConfig
from omnipy.data._display.dimensions import Dimensions as Dimensions
from omnipy.data._display.dimensions import has_height as has_height
from omnipy.data._display.dimensions import has_width as has_width
from omnipy.data._display.frame import empty_frame as empty_frame
from omnipy.data._display.frame import Frame as Frame
from omnipy.data._display.integrations.browser.macosx import \
    OmnipyMacOSXOSAScript as OmnipyMacOSXOSAScript
from omnipy.data._display.integrations.browser.macosx import \
    setup_macosx_browser_integration as setup_macosx_browser_integration
from omnipy.data._display.layout.base import Layout as Layout
from omnipy.data._display.layout.base import PanelDesignDims as PanelDesignDims
from omnipy.data._display.layout.flow.helpers import create_ellipsis_panel as create_ellipsis_panel
from omnipy.data._display.panel.base import FullyRenderedPanel as FullyRenderedPanel
from omnipy.data._display.panel.draft.base import DraftPanel as DraftPanel
from omnipy.data.dataset import Dataset as Dataset
from omnipy.data.helpers import FailedData as FailedData
from omnipy.data.helpers import PendingData as PendingData
from omnipy.data.model import Model as Model
from omnipy.data.typechecks import is_dataset_instance as is_dataset_instance
from omnipy.data.typechecks import is_model_instance as is_model_instance
from omnipy.hub.ui import get_terminal_prompt_height as get_terminal_prompt_height
from omnipy.hub.ui import note_mime_bundle as note_mime_bundle
from omnipy.shared.constants import MAX_PANEL_NESTING_DEPTH as MAX_PANEL_NESTING_DEPTH
from omnipy.shared.constants import MAX_PANELS_HORIZONTALLY as MAX_PANELS_HORIZONTALLY
from omnipy.shared.constants import \
    MAX_PANELS_HORIZONTALLY_DEEPLY_NESTED as MAX_PANELS_HORIZONTALLY_DEEPLY_NESTED
from omnipy.shared.constants import MIN_CROP_WIDTH as MIN_CROP_WIDTH
from omnipy.shared.constants import MIN_PANEL_WIDTH as MIN_PANEL_WIDTH
from omnipy.shared.constants import TITLE_BLANK_LINES as TITLE_BLANK_LINES
from omnipy.shared.enums.colorstyles import AllColorStyles as AllColorStyles
from omnipy.shared.enums.colorstyles import RecommendedColorStyles as RecommendedColorStyles
from omnipy.shared.enums.display import DisplayColorSystem as DisplayColorSystem
from omnipy.shared.enums.display import HorizontalOverflowMode as HorizontalOverflowMode
from omnipy.shared.enums.display import Justify as Justify
from omnipy.shared.enums.display import MaxTitleHeight as MaxTitleHeight
from omnipy.shared.enums.display import PanelDesign as PanelDesign
from omnipy.shared.enums.display import PrettyPrinterLib as PrettyPrinterLib
from omnipy.shared.enums.display import SyntaxLanguage as SyntaxLanguage
from omnipy.shared.enums.display import VerticalOverflowMode as VerticalOverflowMode
from omnipy.shared.enums.ui import BrowserPageUserInterfaceType as BrowserPageUserInterfaceType
from omnipy.shared.enums.ui import BrowserTagUserInterfaceType as BrowserTagUserInterfaceType
from omnipy.shared.enums.ui import BrowserUserInterfaceType as BrowserUserInterfaceType
from omnipy.shared.enums.ui import \
    JupyterEmbeddedUserInterfaceType as JupyterEmbeddedUserInterfaceType
from omnipy.shared.enums.ui import \
    JupyterInBrowserUserInterfaceType as JupyterInBrowserUserInterfaceType
from omnipy.shared.enums.ui import SpecifiedUserInterfaceType as SpecifiedUserInterfaceType
from omnipy.shared.enums.ui import \
    TerminalOutputUserInterfaceType as TerminalOutputUserInterfaceType
from omnipy.shared.enums.ui import UserInterfaceType as UserInterfaceType
from omnipy.shared.protocols.config import IsHtmlUserInterfaceConfig as IsHtmlUserInterfaceConfig
from omnipy.shared.protocols.config import IsUserInterfaceTypeConfig as IsUserInterfaceTypeConfig
from omnipy.shared.typedefs import Method as Method
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import is_package_editable as is_package_editable
from omnipy.util.helpers import min_or_none as min_or_none
from omnipy.util.helpers import takes_input_params_from as takes_input_params_from

P = ParamSpec('P')
_RetT = TypeVar('_RetT')
_RetCovT = TypeVar('_RetCovT', covariant=True)

class _DimsRestatedParams:
    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None

class _DisplayMethodParams(OutputConfig, _DimsRestatedParams): ...

class IsDisplayMethod(Protocol[_RetCovT]):
    def __call__(self, /, width: pyd.NonNegativeInt | None = None, height: pyd.NonNegativeInt | None = None, tab: pyd.NonNegativeInt = 4, indent: pyd.NonNegativeInt = 2, printer: PrettyPrinterLib.Literals = ..., syntax: SyntaxLanguage.Literals | str = ..., freedom: pyd.NonNegativeFloat | None = 2.5, debug: bool = False, ui: SpecifiedUserInterfaceType.Literals = ..., system: DisplayColorSystem.Literals = ..., style: AllColorStyles.Literals | str = ..., bg: bool = False, fonts: tuple[str, ...] = ('Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', 'monospace'), font_size: pyd.NonNegativeInt | None = 14, font_weight: pyd.NonNegativeInt | None = 400, line_height: pyd.NonNegativeFloat | None = 1.25, h_overflow: HorizontalOverflowMode.Literals = ..., v_overflow: VerticalOverflowMode.Literals = ..., panel: PanelDesign.Literals = ..., title_at_top: bool = True, max_title_height: MaxTitleHeight.Literals = ..., min_panel_width: pyd.NonNegativeInt = ..., min_crop_width: pyd.NonNegativeInt = ..., use_min_crop_width: bool = False, max_panels_hor: pyd.NonNegativeInt | None = ..., max_nesting_depth: pyd.NonNegativeInt | None = ..., justify: Justify.Literals = ...) -> _RetCovT: ...

class DisplayMethodKwargs(TypedDict, total=False):
    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None
    tab: pyd.NonNegativeInt
    indent: pyd.NonNegativeInt
    printer: PrettyPrinterLib.Literals
    syntax: SyntaxLanguage.Literals | str
    freedom: pyd.NonNegativeFloat | None
    debug: bool
    ui: SpecifiedUserInterfaceType.Literals
    system: DisplayColorSystem.Literals
    style: AllColorStyles.Literals | str
    bg: bool
    fonts: tuple[str, ...]
    font_size: pyd.NonNegativeInt | None
    font_weight: pyd.NonNegativeInt | None
    line_height: pyd.NonNegativeFloat | None
    h_overflow: HorizontalOverflowMode.Literals
    v_overflow: VerticalOverflowMode.Literals
    panel: PanelDesign.Literals
    title_at_top: bool
    max_title_height: MaxTitleHeight.Literals
    min_panel_width: pyd.NonNegativeInt
    min_crop_width: pyd.NonNegativeInt
    use_min_crop_width: bool
    max_panels_hor: pyd.NonNegativeInt | None
    max_nesting_depth: pyd.NonNegativeInt | None
    justify: Justify.Literals

class IsBaseDisplayMixin(Protocol):
    peek: IsDisplayMethod[Element | None]
    full: IsDisplayMethod[Element | None]
    json: IsDisplayMethod[Element | None]
    browse: IsDisplayMethod[None]

class IsDatabaseDisplayMixin(IsBaseDisplayMixin, Protocol):
    list: IsDisplayMethod[Element | None]

class BaseDisplayMixin(metaclass=abc.ABCMeta):
    def default_repr_to_terminal_str(self, ui_type: TerminalOutputUserInterfaceType.Literals) -> str: ...
    def peek(self, /, *, width: pyd.NonNegativeInt | None = None, height: pyd.NonNegativeInt | None = None, tab: pyd.NonNegativeInt = 4, indent: pyd.NonNegativeInt = 2, printer: PrettyPrinterLib.Literals = ..., syntax: SyntaxLanguage.Literals | str = ..., freedom: pyd.NonNegativeFloat | None = 2.5, debug: bool = False, ui: SpecifiedUserInterfaceType.Literals = ..., system: DisplayColorSystem.Literals = ..., style: AllColorStyles.Literals | str = ..., bg: bool = False, fonts: tuple[str, ...] = ('Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', 'monospace'), font_size: pyd.NonNegativeInt | None = 14, font_weight: pyd.NonNegativeInt | None = 400, line_height: pyd.NonNegativeFloat | None = 1.25, h_overflow: HorizontalOverflowMode.Literals = ..., v_overflow: VerticalOverflowMode.Literals = ..., panel: PanelDesign.Literals = ..., title_at_top: bool = True, max_title_height: MaxTitleHeight.Literals = ..., min_panel_width: pyd.NonNegativeInt = ..., min_crop_width: pyd.NonNegativeInt = ..., use_min_crop_width: bool = False, max_panels_hor: pyd.NonNegativeInt | None = ..., max_nesting_depth: pyd.NonNegativeInt | None = ..., justify: Justify.Literals = ...) -> Element | None: ...
    # def full(self, /, width: pyd.NonNegativeInt | None = None, height: pyd.NonNegativeInt | None = None, tab: pyd.NonNegativeInt = 4, indent: pyd.NonNegativeInt = 2, printer: PrettyPrinterLib.Literals = ..., syntax: SyntaxLanguage.Literals | str = ..., freedom: pyd.NonNegativeFloat | None = 2.5, debug: bool = False, ui: SpecifiedUserInterfaceType.Literals = ..., system: DisplayColorSystem.Literals = ..., style: AllColorStyles.Literals | str = ..., bg: bool = False, fonts: tuple[str, ...] = ('Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', 'monospace'), font_size: pyd.NonNegativeInt | None = 14, font_weight: pyd.NonNegativeInt | None = 400, line_height: pyd.NonNegativeFloat | None = 1.25, h_overflow: HorizontalOverflowMode.Literals = ..., v_overflow: VerticalOverflowMode.Literals = ..., panel: PanelDesign.Literals = ..., title_at_top: bool = True, max_title_height: MaxTitleHeight.Literals = ..., min_panel_width: pyd.NonNegativeInt = ..., min_crop_width: pyd.NonNegativeInt = ..., use_min_crop_width: bool = False, max_panels_hor: pyd.NonNegativeInt | None = ..., max_nesting_depth: pyd.NonNegativeInt | None = ..., justify: Justify.Literals = ...) -> Element | None: ...
    # def json(self, /, width: pyd.NonNegativeInt | None = None, height: pyd.NonNegativeInt | None = None, tab: pyd.NonNegativeInt = 4, indent: pyd.NonNegativeInt = 2, printer: PrettyPrinterLib.Literals = ..., syntax: SyntaxLanguage.Literals | str = ..., freedom: pyd.NonNegativeFloat | None = 2.5, debug: bool = False, ui: SpecifiedUserInterfaceType.Literals = ..., system: DisplayColorSystem.Literals = ..., style: AllColorStyles.Literals | str = ..., bg: bool = False, fonts: tuple[str, ...] = ('Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', 'monospace'), font_size: pyd.NonNegativeInt | None = 14, font_weight: pyd.NonNegativeInt | None = 400, line_height: pyd.NonNegativeFloat | None = 1.25, h_overflow: HorizontalOverflowMode.Literals = ..., v_overflow: VerticalOverflowMode.Literals = ..., panel: PanelDesign.Literals = ..., title_at_top: bool = True, max_title_height: MaxTitleHeight.Literals = ..., min_panel_width: pyd.NonNegativeInt = ..., min_crop_width: pyd.NonNegativeInt = ..., use_min_crop_width: bool = False, max_panels_hor: pyd.NonNegativeInt | None = ..., max_nesting_depth: pyd.NonNegativeInt | None = ..., justify: Justify.Literals = ...) -> Element | None: ...
    # def browse(self, /, width: pyd.NonNegativeInt | None = None, height: pyd.NonNegativeInt | None = None, tab: pyd.NonNegativeInt = 4, indent: pyd.NonNegativeInt = 2, printer: PrettyPrinterLib.Literals = ..., syntax: SyntaxLanguage.Literals | str = ..., freedom: pyd.NonNegativeFloat | None = 2.5, debug: bool = False, ui: SpecifiedUserInterfaceType.Literals = ..., system: DisplayColorSystem.Literals = ..., style: AllColorStyles.Literals | str = ..., bg: bool = False, fonts: tuple[str, ...] = ('Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', 'monospace'), font_size: pyd.NonNegativeInt | None = 14, font_weight: pyd.NonNegativeInt | None = 400, line_height: pyd.NonNegativeFloat | None = 1.25, h_overflow: HorizontalOverflowMode.Literals = ..., v_overflow: VerticalOverflowMode.Literals = ..., panel: PanelDesign.Literals = ..., title_at_top: bool = True, max_title_height: MaxTitleHeight.Literals = ..., min_panel_width: pyd.NonNegativeInt = ..., min_crop_width: pyd.NonNegativeInt = ..., use_min_crop_width: bool = False, max_panels_hor: pyd.NonNegativeInt | None = ..., max_nesting_depth: pyd.NonNegativeInt | None = ..., justify: Justify.Literals = ...) -> None: ...

class ModelDisplayMixin(BaseDisplayMixin): ...

class DatasetDisplayMixin(BaseDisplayMixin):
    def list(self, /, width: pyd.NonNegativeInt | None = None, height: pyd.NonNegativeInt | None = None, tab: pyd.NonNegativeInt = 4, indent: pyd.NonNegativeInt = 2, printer: PrettyPrinterLib.Literals = ..., syntax: SyntaxLanguage.Literals | str = ..., freedom: pyd.NonNegativeFloat | None = 2.5, debug: bool = False, ui: SpecifiedUserInterfaceType.Literals = ..., system: DisplayColorSystem.Literals = ..., style: AllColorStyles.Literals | str = ..., bg: bool = False, fonts: tuple[str, ...] = ('Menlo', 'DejaVu Sans Mono', 'Consolas', 'Courier New', 'monospace'), font_size: pyd.NonNegativeInt | None = 14, font_weight: pyd.NonNegativeInt | None = 400, line_height: pyd.NonNegativeFloat | None = 1.25, h_overflow: HorizontalOverflowMode.Literals = ..., v_overflow: VerticalOverflowMode.Literals = ..., panel: PanelDesign.Literals = ..., title_at_top: bool = True, max_title_height: MaxTitleHeight.Literals = ..., min_panel_width: pyd.NonNegativeInt = ..., min_crop_width: pyd.NonNegativeInt = ..., use_min_crop_width: bool = False, max_panels_hor: pyd.NonNegativeInt | None = ..., max_nesting_depth: pyd.NonNegativeInt | None = ..., justify: Justify.Literals = ...) -> Element | None: ...
