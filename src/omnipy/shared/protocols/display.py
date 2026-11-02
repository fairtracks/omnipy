"""Protocols for the public display API of Omnipy models and datasets."""

from typing import Protocol

from typing_extensions import override

from omnipy.shared.constants import (
    MAX_PANEL_NESTING_DEPTH,
    MAX_PANELS_HORIZONTALLY,
    MIN_CROP_WIDTH,
    MIN_PANEL_WIDTH,
)
from omnipy.shared.enums.colorstyles import AllColorStyles, RecommendedColorStyles
from omnipy.shared.enums.display import (
    DarkBackground,
    DisplayColorSystem,
    HorizontalOverflowMode,
    Justify,
    MaxTitleHeight,
    PanelDesign,
    PrettyPrinterLib,
    SyntaxLanguageSpec,
    VerticalOverflowMode,
)
from omnipy.shared.enums.ui import UserInterfaceType
from omnipy.shared.typing import TYPE_CHECKING
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    from reacton.core import Element


class IsDisplayMethod(Protocol):
    """Protocol for Omnipy display entry points with shared keyword arguments.

    The callback signature mirrors the public display methods on
    :class:`BaseDisplayMixin` and its concrete subclasses.

    Args:
        width: Optional output width in characters.
        height: Optional output height in lines.
        tab: Tab width used by pretty printers.
        indent: Indentation width used by pretty printers.
        printer: Pretty-printer backend selection.
        syntax: Syntax-highlighting language selection.
        freedom: Proportional layout flexibility for formatting.
        debug: Enables debug-oriented display details when supported.
        ui: Target user-interface type.
        system: Terminal/browser color-system selection.
        style: Color style or theme.
        dark: Dark-background preference mode.
        bg: Whether to draw an explicit background.
        fonts: Preferred font families for HTML output.
        font_size: Font size for HTML output.
        font_weight: Font weight for HTML output.
        line_height: Line-height multiplier for HTML output.
        h_overflow: Horizontal-overflow handling mode.
        v_overflow: Vertical-overflow handling mode.
        panel: Panel-design mode.
        title_at_top: Whether panel titles are rendered above content.
        max_title_height: Maximum number of title lines.
        min_panel_width: Minimum panel width.
        min_crop_width: Minimum cropping width for constrained layouts.
        use_min_crop_width: Whether ``min_crop_width`` should be enforced.
        max_panels_hor: Maximum number of horizontal panels.
        max_nesting_depth: Maximum nested panel depth.
        justify: Panel-content justification mode.

    Returns:
        A UI-specific display result. Narrower protocols define the concrete
        return type for each display variant.

    Raises:
        NotImplementedError: Raised by concrete implementations when the
            protocol contract is not implemented.

    Examples:
        >>> def preview(*, ui=UserInterfaceType.AUTO, **kwargs) -> object:
        ...     return None
    """

    # Forward references for the non-trivial __call__ parameters are needed
    # for mkdocstrings/griffe extension (omnipy.util.griffe_extension:
    # UseDynamicSignatureForSpecificFunctions) to work correctly.
    def __call__(
        self,
        *,
        width: 'pyd.NonNegativeInt | None' = None,
        height: 'pyd.NonNegativeInt | None' = None,
        tab: 'pyd.NonNegativeInt' = 4,
        indent: 'pyd.NonNegativeInt' = 2,
        printer: 'PrettyPrinterLib.Literals' = PrettyPrinterLib.AUTO,
        syntax: 'SyntaxLanguageSpec.Literals | str' = SyntaxLanguageSpec.AUTO,
        freedom: 'pyd.NonNegativeFloat | None' = 2.5,
        debug: bool = False,
        ui: 'UserInterfaceType.Literals' = UserInterfaceType.AUTO,
        system: 'DisplayColorSystem.Literals' = DisplayColorSystem.AUTO,
        style: 'AllColorStyles.Literals | str' = RecommendedColorStyles.AUTO,
        dark: DarkBackground.Literals = DarkBackground.AUTO,
        bg: bool = False,
        fonts: tuple[str, ...] = (
            'Menlo',
            'DejaVu Sans Mono',
            'Consolas',
            'Courier New',
            'monospace',
        ),
        font_size: 'pyd.NonNegativeFloat | None' = 14,
        font_weight: 'pyd.NonNegativeInt | None' = 400,
        line_height: 'pyd.NonNegativeFloat | None' = 1.25,
        h_overflow: 'HorizontalOverflowMode.Literals' = HorizontalOverflowMode.ELLIPSIS,
        v_overflow: 'VerticalOverflowMode.Literals' = VerticalOverflowMode.ELLIPSIS_BOTTOM,
        panel: 'PanelDesign.Literals' = PanelDesign.TABLE,
        title_at_top: bool = True,
        max_title_height: 'MaxTitleHeight.Literals' = MaxTitleHeight.AUTO,
        min_panel_width: 'pyd.NonNegativeInt' = MIN_PANEL_WIDTH,
        min_crop_width: 'pyd.NonNegativeInt' = MIN_CROP_WIDTH,
        use_min_crop_width: bool = False,
        max_panels_hor: 'pyd.NonNegativeInt | None' = MAX_PANELS_HORIZONTALLY,
        max_nesting_depth: 'pyd.NonNegativeInt | None' = MAX_PANEL_NESTING_DEPTH,
        justify: 'Justify.Literals' = Justify.LEFT,
    ) -> object: ...


class IsDisplayMethodMaybeReturnElement(IsDisplayMethod, Protocol):
    """Display callback protocol for methods returning HTML element or ``None``.

    Args:
        Same keyword-only arguments as :class:`IsDisplayMethod`.

    Returns:
        ``Element | None`` depending on UI backend and execution context.

    Raises:
        NotImplementedError: Raised by concrete implementations when this
            callback protocol is not implemented.

    Examples:
        >>> def show(*, ui=UserInterfaceType.AUTO, **kwargs) -> Element | None:
        ...     return None
    """

    @override
    def __call__(
        self,
        *,
        width: 'pyd.NonNegativeInt | None' = None,
        height: 'pyd.NonNegativeInt | None' = None,
        tab: 'pyd.NonNegativeInt' = 4,
        indent: 'pyd.NonNegativeInt' = 2,
        printer: 'PrettyPrinterLib.Literals' = PrettyPrinterLib.AUTO,
        syntax: 'SyntaxLanguageSpec.Literals | str' = SyntaxLanguageSpec.AUTO,
        freedom: 'pyd.NonNegativeFloat | None' = 2.5,
        debug: bool = False,
        ui: 'UserInterfaceType.Literals' = UserInterfaceType.AUTO,
        system: 'DisplayColorSystem.Literals' = DisplayColorSystem.AUTO,
        style: 'AllColorStyles.Literals | str' = RecommendedColorStyles.AUTO,
        dark: DarkBackground.Literals = DarkBackground.AUTO,
        bg: bool = False,
        fonts: tuple[str, ...] = (
            'Menlo',
            'DejaVu Sans Mono',
            'Consolas',
            'Courier New',
            'monospace',
        ),
        font_size: 'pyd.NonNegativeFloat | None' = 14,
        font_weight: 'pyd.NonNegativeInt | None' = 400,
        line_height: 'pyd.NonNegativeFloat | None' = 1.25,
        h_overflow: 'HorizontalOverflowMode.Literals' = HorizontalOverflowMode.ELLIPSIS,
        v_overflow: 'VerticalOverflowMode.Literals' = VerticalOverflowMode.ELLIPSIS_BOTTOM,
        panel: 'PanelDesign.Literals' = PanelDesign.TABLE,
        title_at_top: bool = True,
        max_title_height: 'MaxTitleHeight.Literals' = MaxTitleHeight.AUTO,
        min_panel_width: 'pyd.NonNegativeInt' = MIN_PANEL_WIDTH,
        min_crop_width: 'pyd.NonNegativeInt' = MIN_CROP_WIDTH,
        use_min_crop_width: bool = False,
        max_panels_hor: 'pyd.NonNegativeInt | None' = MAX_PANELS_HORIZONTALLY,
        max_nesting_depth: 'pyd.NonNegativeInt | None' = MAX_PANEL_NESTING_DEPTH,
        justify: 'Justify.Literals' = Justify.LEFT,
    ) -> 'Element | None': ...


class IsDisplayMethodReturnNone(IsDisplayMethod, Protocol):
    """Display callback protocol for methods with side effects only.

    Args:
        Same keyword-only arguments as :class:`IsDisplayMethod`.

    Returns:
        ``None``.

    Raises:
        NotImplementedError: Raised by concrete implementations when this
            callback protocol is not implemented.

    Examples:
        >>> def open_browser(*, ui=UserInterfaceType.AUTO, **kwargs) -> None:
        ...     return None
    """

    @override
    def __call__(
        self,
        *,
        width: 'pyd.NonNegativeInt | None' = None,
        height: 'pyd.NonNegativeInt | None' = None,
        tab: 'pyd.NonNegativeInt' = 4,
        indent: 'pyd.NonNegativeInt' = 2,
        printer: 'PrettyPrinterLib.Literals' = PrettyPrinterLib.AUTO,
        syntax: 'SyntaxLanguageSpec.Literals | str' = SyntaxLanguageSpec.AUTO,
        freedom: 'pyd.NonNegativeFloat | None' = 2.5,
        debug: bool = False,
        ui: 'UserInterfaceType.Literals' = UserInterfaceType.AUTO,
        system: 'DisplayColorSystem.Literals' = DisplayColorSystem.AUTO,
        style: 'AllColorStyles.Literals | str' = RecommendedColorStyles.AUTO,
        dark: DarkBackground.Literals = DarkBackground.AUTO,
        bg: bool = False,
        fonts: tuple[str, ...] = (
            'Menlo',
            'DejaVu Sans Mono',
            'Consolas',
            'Courier New',
            'monospace',
        ),
        font_size: 'pyd.NonNegativeFloat | None' = 14,
        font_weight: 'pyd.NonNegativeInt | None' = 400,
        line_height: 'pyd.NonNegativeFloat | None' = 1.25,
        h_overflow: 'HorizontalOverflowMode.Literals' = HorizontalOverflowMode.ELLIPSIS,
        v_overflow: 'VerticalOverflowMode.Literals' = VerticalOverflowMode.ELLIPSIS_BOTTOM,
        panel: 'PanelDesign.Literals' = PanelDesign.TABLE,
        title_at_top: bool = True,
        max_title_height: 'MaxTitleHeight.Literals' = MaxTitleHeight.AUTO,
        min_panel_width: 'pyd.NonNegativeInt' = MIN_PANEL_WIDTH,
        min_crop_width: 'pyd.NonNegativeInt' = MIN_CROP_WIDTH,
        use_min_crop_width: bool = False,
        max_panels_hor: 'pyd.NonNegativeInt | None' = MAX_PANELS_HORIZONTALLY,
        max_nesting_depth: 'pyd.NonNegativeInt | None' = MAX_PANEL_NESTING_DEPTH,
        justify: 'Justify.Literals' = Justify.LEFT,
    ) -> None: ...


class IsDisplayMethodReturnStr(IsDisplayMethod, Protocol):
    """Display callback protocol for methods returning terminal/browser text.

    Args:
        Same keyword-only arguments as :class:`IsDisplayMethod`.

    Returns:
        Rendered textual output as a ``str``.

    Raises:
        NotImplementedError: Raised by concrete implementations when this
            callback protocol is not implemented.

    Examples:
        >>> def docs(*, ui=UserInterfaceType.BROWSER_TAG, **kwargs) -> str:
        ...     return '<pre>...</pre>'
    """

    @override
    def __call__(
        self,
        *,
        width: 'pyd.NonNegativeInt | None' = None,
        height: 'pyd.NonNegativeInt | None' = None,
        tab: 'pyd.NonNegativeInt' = 4,
        indent: 'pyd.NonNegativeInt' = 2,
        printer: 'PrettyPrinterLib.Literals' = PrettyPrinterLib.AUTO,
        syntax: 'SyntaxLanguageSpec.Literals | str' = SyntaxLanguageSpec.AUTO,
        freedom: 'pyd.NonNegativeFloat | None' = 2.5,
        debug: bool = False,
        ui: 'UserInterfaceType.Literals' = UserInterfaceType.AUTO,
        system: 'DisplayColorSystem.Literals' = DisplayColorSystem.AUTO,
        style: 'AllColorStyles.Literals | str' = RecommendedColorStyles.AUTO,
        dark: DarkBackground.Literals = DarkBackground.AUTO,
        bg: bool = False,
        fonts: tuple[str, ...] = (
            'Menlo',
            'DejaVu Sans Mono',
            'Consolas',
            'Courier New',
            'monospace',
        ),
        font_size: 'pyd.NonNegativeFloat | None' = 14,
        font_weight: 'pyd.NonNegativeInt | None' = 400,
        line_height: 'pyd.NonNegativeFloat | None' = 1.25,
        h_overflow: 'HorizontalOverflowMode.Literals' = HorizontalOverflowMode.ELLIPSIS,
        v_overflow: 'VerticalOverflowMode.Literals' = VerticalOverflowMode.ELLIPSIS_BOTTOM,
        panel: 'PanelDesign.Literals' = PanelDesign.TABLE,
        title_at_top: bool = True,
        max_title_height: 'MaxTitleHeight.Literals' = MaxTitleHeight.AUTO,
        min_panel_width: 'pyd.NonNegativeInt' = MIN_PANEL_WIDTH,
        min_crop_width: 'pyd.NonNegativeInt' = MIN_CROP_WIDTH,
        use_min_crop_width: bool = False,
        max_panels_hor: 'pyd.NonNegativeInt | None' = MAX_PANELS_HORIZONTALLY,
        max_nesting_depth: 'pyd.NonNegativeInt | None' = MAX_PANEL_NESTING_DEPTH,
        justify: 'Justify.Literals' = Justify.LEFT,
    ) -> str: ...


class IsBaseDisplayMixin(Protocol):
    """Protocol for the shared public display API of models and datasets.

    Args:
        Not applicable. This protocol specifies attributes and call
        signatures for mixin implementers.

    Returns:
        Not applicable.

    Raises:
        AttributeError: When a required display method attribute is missing on
            a concrete implementation.

    Examples:
        >>> def render_preview(data: IsBaseDisplayMixin) -> None:
        ...     data.peek()
    """

    peek: IsDisplayMethodMaybeReturnElement
    full: IsDisplayMethodMaybeReturnElement
    json: IsDisplayMethodMaybeReturnElement
    browse: IsDisplayMethodReturnNone
    _docs: IsDisplayMethodReturnStr


class IsDatasetDisplayMixin(IsBaseDisplayMixin, Protocol):
    """Protocol extension for dataset-specific display behavior.

    Args:
        Not applicable. This protocol extends :class:`IsBaseDisplayMixin`
        with dataset-specific display entry points.

    Returns:
        Not applicable.

    Raises:
        AttributeError: When dataset-specific display members are missing on
            a concrete implementation.

    Examples:
        >>> def render_summary(dataset: IsDatasetDisplayMixin) -> None:
        ...     dataset.list()
    """

    list: IsDisplayMethodMaybeReturnElement
