from textwrap import dedent
from typing import Literal

from typing_extensions import assert_never

from omnipy.shared.enums.display import DisplayColorSystem
from omnipy.util.literal_enum import LiteralEnum

_ANSI_TEXT = dedent("""
    The ANSI {variant} color setting from the Rich library is set as default
    for terminals with a {variant} background and low number of supported
    colors. This is out of pragmatism, as it makes use of the predefined
    colors of the terminal instead of overriding with a predefined color
    style.
    """)

_SELENIZED_TEXT = dedent("""
    The Omnipy Selenized styles are based on the Selenized color scheme by
    Jan Warchoł (https://github.com/jan-warchol/selenized).

    Features:
    - Easy on the eyes.
    - Beautiful, vibrant and easily distinguishable accent colors.
    - Great readability and better compatibility with Web Content
      Accessibility Guidelines.

    The Omnipy adaptations features slightly less contrast for comment
    colors, which is offset by the use of italics to make them stand out.
    These color styles work well with transparent backgrounds to blend in
    with the current terminal theme. For best results, you should change
    the background color of the terminal (or the complete color theme) to
    align with the Omnipy Selenized styles. """)


class RecommendedColorStyles(LiteralEnum[str]):
    """
    Recommended color styles for syntax highlighting, provided through the
    Pygments and Rich libraries.

    The ANSI color styles are provided to make Omnipy work ok on a wider
    range of terminals, but they are not recommended for use in the long
    run. For best results, you should switch to the light or white variants
    of the Omnipy Selenized styles, or to another color style of your
    choice. """

    Literals = Literal['auto',
                       'ansi-dark',
                       'ansi-light',
                       'omnipy-selenized-black',
                       'omnipy-selenized-dark',
                       'omnipy-selenized-light',
                       'omnipy-selenized-white']

    AUTO: Literal['auto'] = 'auto'
    """
    The default color style, which is automatically replaced with one of the
    other recommended styles based on the color system, dark background
    and transparent background settings.

    ANSI color styles are selected for color systems with fewer than 256
    colors. Otherwise, the Omnipy Selenized styles are selected based on
    the dark background and transparent background settings.

    All recommended styles will automatically replace themselves with other
    recommended styles if the color system or background settings change.
    If you want to fix a specific color style, you should use one of the
    other (non-recommended) styles directly.
    """

    ANSI_DARK: Literal['ansi-dark'] = 'ansi-dark'
    f"""
    {_ANSI_TEXT.format(variant='dark')}
    """

    ANSI_LIGHT: Literal['ansi-light'] = 'ansi-light'
    f"""
    {_ANSI_TEXT.format(variant='light')}Even though the light variant is
    defined for light backgrounds, you may find the ANSI dark variant
    slightly more readable across both light and dark terminal themes.
    """

    OMNIPY_SELENIZED_BLACK: Literal['omnipy-selenized-black'] = 'omnipy-selenized-black'
    f"""
    {_SELENIZED_TEXT}
    Black variant: A slightly soft dark theme with an almost black
    background, suitable also on a fully black background.
    """

    OMNIPY_SELENIZED_DARK: Literal['omnipy-selenized-dark'] = 'omnipy-selenized-dark'
    f"""
    {_SELENIZED_TEXT}
    Dark variant: A dark theme on a dark bluish background, a bit harsh on a
    fully black background.
    """

    OMNIPY_SELENIZED_LIGHT: Literal['omnipy-selenized-light'] = 'omnipy-selenized-light'
    f"""
    {_SELENIZED_TEXT}
    Light variant: A soft light theme on an off-white background, suitable
    also on a fully white background for a softer feel.
    """

    OMNIPY_SELENIZED_WHITE: Literal['omnipy-selenized-white'] = 'omnipy-selenized-white'
    f"""
    {_SELENIZED_TEXT}
    White variant: A light theme on a fully white background.
    """

    # Methods

    @classmethod
    def get_default_style(
        cls,
        color_system: DisplayColorSystem.Literals,
        dark_background: bool,
        solid_background: bool,
    ) -> 'RecommendedColorStyles.Literals':
        """
        Returns the default color style for the given color system.
        """
        match (color_system, dark_background, solid_background):
            case (DisplayColorSystem.ANSI_256 | DisplayColorSystem.ANSI_RGB, False, False):
                return cls.OMNIPY_SELENIZED_WHITE
            case (DisplayColorSystem.ANSI_256 | DisplayColorSystem.ANSI_RGB, False, True):
                return cls.OMNIPY_SELENIZED_LIGHT
            case (DisplayColorSystem.ANSI_256 | DisplayColorSystem.ANSI_RGB, True, False):
                return cls.OMNIPY_SELENIZED_BLACK
            case (DisplayColorSystem.ANSI_256 | DisplayColorSystem.ANSI_RGB, True, True):
                return cls.OMNIPY_SELENIZED_DARK
            case _, False, _:
                return cls.ANSI_LIGHT
            case _, True, _:
                return cls.ANSI_DARK
            case _ as never:
                assert_never(never)  # type: ignore[arg-type] # Unsure why mypy fails here


_GENERAL_T16_COLOR_STYLE_DOCSTRING = dedent("""\
    {description} color styles based on the Base16 color
    framework and auto-imported from the [color scheme repository]
    (https://github.com/tinted-theming/schemes) of the [Tinted Theming]
    (https://github.com/tinted-theming) project. The Base16 color framework
    was designed by Chris Kempson (https://github.com/chriskempson/base16).

    For a gallery of the "Tinted Theming" Base16 color schemes, see
    https://tinted-theming.github.io/tinted-gallery/.

    The mapping of the Base16 color framework onto the Pygments library is
    Omnipy-specific, and available as the function
    `get_styles_from_base16_colors()` in the
    `omnipy.data._display.styles.dynamic_styles` module.""")

_COLOR_CONTRAST_TEXT = dedent("""\
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/), as determined with the "color-contrast"
    Python library (https://github.com/ZugBahnHof/color-contrast).""")


class DarkHighContrastTintedThemingBase16ColorStyles(LiteralEnum[str]):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='Dark, high-contrast')}

    These styles have high-level contrast that conform to {_COLOR_CONTRAST_TEXT}
    """
    Literals = Literal['0x96f-t16',
                       '3024-t16',
                       'apathy-t16',
                       'ashes-t16',
                       'atelier-cave-t16',
                       'atelier-dune-t16',
                       'atelier-estuary-t16',
                       'atelier-forest-t16',
                       'atelier-heath-t16',
                       'atelier-lakeside-t16',
                       'atelier-plateau-t16',
                       'atelier-savanna-t16',
                       'atelier-seaside-t16',
                       'atelier-sulphurpool-t16',
                       'atlas-t16',
                       'ayu-dark-t16',
                       'ayu-mirage-t16',
                       'aztec-t16',
                       'bespin-t16',
                       'black-metal-bathory-t16',
                       'black-metal-burzum-t16',
                       'black-metal-dark-funeral-t16',
                       'black-metal-gorgoroth-t16',
                       'black-metal-immortal-t16',
                       'black-metal-khold-t16',
                       'black-metal-marduk-t16',
                       'black-metal-mayhem-t16',
                       'black-metal-nile-t16',
                       'black-metal-venom-t16',
                       'black-metal-t16',
                       'blueforest-t16',
                       'blueish-t16',
                       'brewer-t16',
                       'bright-t16',
                       'caroline-t16',
                       'catppuccin-frappe-t16',
                       'catppuccin-macchiato-t16',
                       'catppuccin-mocha-t16',
                       'charcoal-dark-t16',
                       'chalk-t16',
                       'chicago-night-t16',
                       'chinoiserie-midnight-t16',
                       'chinoiserie-morandi-t16',
                       'chinoiserie-night-t16',
                       'circus-t16',
                       'classic-dark-t16',
                       'codeschool-t16',
                       'colors-t16',
                       'da-one-black-t16',
                       'da-one-gray-t16',
                       'da-one-ocean-t16',
                       'da-one-sea-t16',
                       'danqing-t16',
                       'darcula-t16',
                       'darkmoss-t16',
                       'darktooth-t16',
                       'darkviolet-t16',
                       'decaf-t16',
                       'deep-oceanic-next-t16',
                       'default-dark-t16',
                       'digital-rain-t16',
                       'dracula-t16',
                       'edge-dark-t16',
                       'eighties-t16',
                       'embers-t16',
                       'equilibrium-dark-t16',
                       'equilibrium-gray-dark-t16',
                       'espresso-t16',
                       'evenok-dark-t16',
                       'everforest-dark-hard-t16',
                       'everforest-dark-soft-t16',
                       'everforest-t16',
                       'flat-t16',
                       'framer-t16',
                       'gigavolt-t16',
                       'github-dark-t16',
                       'google-dark-t16',
                       'gotham-t16',
                       'grayscale-dark-t16',
                       'greenscreen-t16',
                       'gruber-t16',
                       'gruvbox-dark-hard-t16',
                       'gruvbox-dark-medium-t16',
                       'gruvbox-dark-pale-t16',
                       'gruvbox-dark-soft-t16',
                       'gruvbox-dark-t16',
                       'gruvbox-material-dark-hard-t16',
                       'gruvbox-material-dark-medium-t16',
                       'gruvbox-material-dark-soft-t16',
                       'hardcore-t16',
                       'hardhacker-t16',
                       'harmonic16-dark-t16',
                       'heetch-t16',
                       'helios-t16',
                       'hopscotch-t16',
                       'horizon-dark-t16',
                       'horizon-terminal-dark-t16',
                       'humanoid-dark-t16',
                       'ia-dark-t16',
                       'irblack-t16',
                       'isotope-t16',
                       'jabuti-t16',
                       'kanagawa-dragon-t16',
                       'kanagawa-t16',
                       'katy-t16',
                       'kimber-t16',
                       'linux-vt-t16',
                       'macintosh-t16',
                       'marrakesh-t16',
                       'materia-t16',
                       'material-darker-t16',
                       'material-palenight-t16',
                       'material-t16',
                       'measured-dark-t16',
                       'mellow-purple-t16',
                       'mocha-t16',
                       'monokai-t16',
                       'moonlight-t16',
                       'mountain-t16',
                       'nebula-t16',
                       'nord-t16',
                       'nova-t16',
                       'ocean-t16',
                       'oceanicnext-t16',
                       'onedark-dark-t16',
                       'onedark-t16',
                       'outrun-dark-t16',
                       'oxocarbon-dark-t16',
                       'pandora-t16',
                       'paraiso-t16',
                       'pasque-t16',
                       'penumbra-dark-contrast-plus-plus-t16',
                       'penumbra-dark-contrast-plus-t16',
                       'penumbra-dark-t16',
                       'phd-t16',
                       'pinky-t16',
                       'pop-t16',
                       'porple-t16',
                       'precious-dark-eleven-t16',
                       'precious-dark-fifteen-t16',
                       'primer-dark-dimmed-t16',
                       'primer-dark-t16',
                       'purpledream-t16',
                       'qualia-t16',
                       'railscasts-t16',
                       'rebecca-t16',
                       'rose-pine-moon-t16',
                       'rose-pine-t16',
                       'saga-t16',
                       'sandcastle-t16',
                       'selenized-black-t16',
                       'selenized-dark-t16',
                       'seti-t16',
                       'shades-of-purple-t16',
                       'shadesmear-dark-t16',
                       'silk-dark-t16',
                       'snazzy-t16',
                       'solarflare-t16',
                       'solarized-dark-t16',
                       'spaceduck-t16',
                       'spacemacs-t16',
                       'sparky-t16',
                       'standardized-dark-t16',
                       'stella-t16',
                       'summerfruit-dark-t16',
                       'synth-midnight-dark-t16',
                       'tango-t16',
                       'tender-t16',
                       'terracotta-dark-t16',
                       'tokyo-city-dark-t16',
                       'tokyo-city-terminal-dark-t16',
                       'tokyo-night-dark-t16',
                       'tokyo-night-storm-t16',
                       'tokyodark-terminal-t16',
                       'tokyodark-t16',
                       'tomorrow-night-eighties-t16',
                       'tomorrow-night-t16',
                       'tube-t16',
                       'twilight-t16',
                       'unikitty-dark-t16',
                       'unikitty-reversible-t16',
                       'uwunicorn-t16',
                       'valua-t16',
                       'vesper-t16',
                       'vice-t16',
                       'windows-10-t16',
                       'windows-95-t16',
                       'windows-highcontrast-t16',
                       'windows-nt-t16',
                       'woodland-t16',
                       'xcode-dusk-t16',
                       'zenbones-t16',
                       'zenburn-t16',
                       'random-t16-dark-high']

    NUMBER_0X96F_T16: Literal['0x96f-t16'] = '0x96f-t16'
    """
    0x96f: Base-16 color style by "Filip Janevski".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    NUMBER_3024_T16: Literal['3024-t16'] = '3024-t16'
    """
    3024: Base-16 color style by "Jan T. Sott".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    APATHY_T16: Literal['apathy-t16'] = 'apathy-t16'
    """
    Apathy: Base-16 color style by "Jannik Siebert".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ASHES_T16: Literal['ashes-t16'] = 'ashes-t16'
    """
    Ashes: Base-16 color style by "Jannik Siebert".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_CAVE_T16: Literal['atelier-cave-t16'] = 'atelier-cave-t16'
    """
    Atelier Cave: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_DUNE_T16: Literal['atelier-dune-t16'] = 'atelier-dune-t16'
    """
    Atelier Dune: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_ESTUARY_T16: Literal['atelier-estuary-t16'] = 'atelier-estuary-t16'
    """
    Atelier Estuary: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_FOREST_T16: Literal['atelier-forest-t16'] = 'atelier-forest-t16'
    """
    Atelier Forest: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_HEATH_T16: Literal['atelier-heath-t16'] = 'atelier-heath-t16'
    """
    Atelier Heath: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_LAKESIDE_T16: Literal['atelier-lakeside-t16'] = 'atelier-lakeside-t16'
    """
    Atelier Lakeside: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_PLATEAU_T16: Literal['atelier-plateau-t16'] = 'atelier-plateau-t16'
    """
    Atelier Plateau: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_SAVANNA_T16: Literal['atelier-savanna-t16'] = 'atelier-savanna-t16'
    """
    Atelier Savanna: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_SEASIDE_T16: Literal['atelier-seaside-t16'] = 'atelier-seaside-t16'
    """
    Atelier Seaside: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_SULPHURPOOL_T16: Literal['atelier-sulphurpool-t16'] = 'atelier-sulphurpool-t16'
    """
    Atelier Sulphurpool: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATLAS_T16: Literal['atlas-t16'] = 'atlas-t16'
    """
    Atlas: Base-16 color style by "Alex Lende".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    AYU_DARK_T16: Literal['ayu-dark-t16'] = 'ayu-dark-t16'
    """
    Ayu Dark: Base-16 color style by "Khue Nguyen".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    AYU_MIRAGE_T16: Literal['ayu-mirage-t16'] = 'ayu-mirage-t16'
    """
    Ayu Mirage: Base-16 color style by "Khue Nguyen".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    AZTEC_T16: Literal['aztec-t16'] = 'aztec-t16'
    """
    Aztec: Base-16 color style by "TheNeverMan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BESPIN_T16: Literal['bespin-t16'] = 'bespin-t16'
    """
    Bespin: Base-16 color style by "Jan T. Sott".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_BATHORY_T16: Literal['black-metal-bathory-t16'] = 'black-metal-bathory-t16'
    """
    Black Metal (Bathory): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_BURZUM_T16: Literal['black-metal-burzum-t16'] = 'black-metal-burzum-t16'
    """
    Black Metal (Burzum): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_DARK_FUNERAL_T16: Literal[
        'black-metal-dark-funeral-t16'] = 'black-metal-dark-funeral-t16'
    """
    Black Metal (Dark Funeral): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_GORGOROTH_T16: Literal['black-metal-gorgoroth-t16'] = 'black-metal-gorgoroth-t16'
    """
    Black Metal (Gorgoroth): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_IMMORTAL_T16: Literal['black-metal-immortal-t16'] = 'black-metal-immortal-t16'
    """
    Black Metal (Immortal): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_KHOLD_T16: Literal['black-metal-khold-t16'] = 'black-metal-khold-t16'
    """
    Black Metal (Khold): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_MARDUK_T16: Literal['black-metal-marduk-t16'] = 'black-metal-marduk-t16'
    """
    Black Metal (Marduk): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_MAYHEM_T16: Literal['black-metal-mayhem-t16'] = 'black-metal-mayhem-t16'
    """
    Black Metal (Mayhem): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_NILE_T16: Literal['black-metal-nile-t16'] = 'black-metal-nile-t16'
    """
    Black Metal (Nile): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_VENOM_T16: Literal['black-metal-venom-t16'] = 'black-metal-venom-t16'
    """
    Black Metal (Venom): Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLACK_METAL_T16: Literal['black-metal-t16'] = 'black-metal-t16'
    """
    Black Metal: Base-16 color style by "metalelf0".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLUEFOREST_T16: Literal['blueforest-t16'] = 'blueforest-t16'
    """
    Blue Forest: Base-16 color style by "alonsodomin".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BLUEISH_T16: Literal['blueish-t16'] = 'blueish-t16'
    """
    Blueish: Base-16 color style by "Ben Mayoras".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BREWER_T16: Literal['brewer-t16'] = 'brewer-t16'
    """
    Brewer: Base-16 color style by "Timothée Poisot".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    BRIGHT_T16: Literal['bright-t16'] = 'bright-t16'
    """
    Bright: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CAROLINE_T16: Literal['caroline-t16'] = 'caroline-t16'
    """
    caroline: Base-16 color style by "ed".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CATPPUCCIN_FRAPPE_T16: Literal['catppuccin-frappe-t16'] = 'catppuccin-frappe-t16'
    """
    Catppuccin Frappe: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CATPPUCCIN_MACCHIATO_T16: Literal['catppuccin-macchiato-t16'] = 'catppuccin-macchiato-t16'
    """
    Catppuccin Macchiato: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CATPPUCCIN_MOCHA_T16: Literal['catppuccin-mocha-t16'] = 'catppuccin-mocha-t16'
    """
    Catppuccin Mocha: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHALK_T16: Literal['chalk-t16'] = 'chalk-t16'
    """
    Chalk: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHARCOAL_DARK_T16: Literal['charcoal-dark-t16'] = 'charcoal-dark-t16'
    """
    Charcoal Dark: Base-16 color style by "Mubin Muhammad".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHICAGO_NIGHT_T16: Literal['chicago-night-t16'] = 'chicago-night-t16'
    """
    Chicago Night: Base-16 color style by "Wendell, Ryan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHINOISERIE_MIDNIGHT_T16: Literal['chinoiserie-midnight-t16'] = 'chinoiserie-midnight-t16'
    """
    Chinoiserie Midnight: Base-16 color style by "Di Wang".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHINOISERIE_MORANDI_T16: Literal['chinoiserie-morandi-t16'] = 'chinoiserie-morandi-t16'
    """
    Chinoiserie Morandi: Base-16 color style by "Di Wang".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHINOISERIE_NIGHT_T16: Literal['chinoiserie-night-t16'] = 'chinoiserie-night-t16'
    """
    Chinoiserie Night: Base-16 color style by "Di Wang".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CIRCUS_T16: Literal['circus-t16'] = 'circus-t16'
    """
    Circus: Base-16 color style by "Stephan Boyer".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CLASSIC_DARK_T16: Literal['classic-dark-t16'] = 'classic-dark-t16'
    """
    Classic Dark: Base-16 color style by "Jason Heeris".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CODESCHOOL_T16: Literal['codeschool-t16'] = 'codeschool-t16'
    """
    Codeschool: Base-16 color style by "blockloop".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    COLORS_T16: Literal['colors-t16'] = 'colors-t16'
    """
    Colors: Base-16 color style by "mrmrs".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DA_ONE_BLACK_T16: Literal['da-one-black-t16'] = 'da-one-black-t16'
    """
    Da One Black: Base-16 color style by "NNB".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DA_ONE_GRAY_T16: Literal['da-one-gray-t16'] = 'da-one-gray-t16'
    """
    Da One Gray: Base-16 color style by "NNB".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DA_ONE_OCEAN_T16: Literal['da-one-ocean-t16'] = 'da-one-ocean-t16'
    """
    Da One Ocean: Base-16 color style by "NNB".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DA_ONE_SEA_T16: Literal['da-one-sea-t16'] = 'da-one-sea-t16'
    """
    Da One Sea: Base-16 color style by "NNB".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DANQING_T16: Literal['danqing-t16'] = 'danqing-t16'
    """
    DanQing: Base-16 color style by "Wenhan Zhu".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DARCULA_T16: Literal['darcula-t16'] = 'darcula-t16'
    """
    Darcula: Base-16 color style by "jetbrains".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DARKMOSS_T16: Literal['darkmoss-t16'] = 'darkmoss-t16'
    """
    darkmoss: Base-16 color style by "Gabriel Avanzi".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DARKTOOTH_T16: Literal['darktooth-t16'] = 'darktooth-t16'
    """
    Darktooth: Base-16 color style by "Jason Milkins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DARKVIOLET_T16: Literal['darkviolet-t16'] = 'darkviolet-t16'
    """
    Dark Violet: Base-16 color style by "ruler501".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DECAF_T16: Literal['decaf-t16'] = 'decaf-t16'
    """
    Decaf: Base-16 color style by "Alex Mirrington".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DEEP_OCEANIC_NEXT_T16: Literal['deep-oceanic-next-t16'] = 'deep-oceanic-next-t16'
    """
    Deep Oceanic Next: Base-16 color style by "spearkkk".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DEFAULT_DARK_T16: Literal['default-dark-t16'] = 'default-dark-t16'
    """
    Default Dark: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DIGITAL_RAIN_T16: Literal['digital-rain-t16'] = 'digital-rain-t16'
    """
    Digital Rain: Base-16 color style by "Nathan Byrd".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DRACULA_T16: Literal['dracula-t16'] = 'dracula-t16'
    """
    Dracula: Base-16 color style by "Jamy Golden".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EDGE_DARK_T16: Literal['edge-dark-t16'] = 'edge-dark-t16'
    """
    Edge Dark: Base-16 color style by "cjayross".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EIGHTIES_T16: Literal['eighties-t16'] = 'eighties-t16'
    """
    Eighties: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EMBERS_T16: Literal['embers-t16'] = 'embers-t16'
    """
    Embers: Base-16 color style by "Jannik Siebert".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EQUILIBRIUM_DARK_T16: Literal['equilibrium-dark-t16'] = 'equilibrium-dark-t16'
    """
    Equilibrium Dark: Base-16 color style by "Carlo Abelli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EQUILIBRIUM_GRAY_DARK_T16: Literal['equilibrium-gray-dark-t16'] = 'equilibrium-gray-dark-t16'
    """
    Equilibrium Gray Dark: Base-16 color style by "Carlo Abelli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ESPRESSO_T16: Literal['espresso-t16'] = 'espresso-t16'
    """
    Espresso: Base-16 color style by "Unknown. Maintained by Alex
    Mirrington".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EVENOK_DARK_T16: Literal['evenok-dark-t16'] = 'evenok-dark-t16'
    """
    Evenok Dark: Base-16 color style by "Mekeor Melire".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EVERFOREST_DARK_HARD_T16: Literal['everforest-dark-hard-t16'] = 'everforest-dark-hard-t16'
    """
    Everforest Dark Hard: Base-16 color style by "Sainnhe Park".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EVERFOREST_DARK_SOFT_T16: Literal['everforest-dark-soft-t16'] = 'everforest-dark-soft-t16'
    """
    Everforest Dark Soft: Base-16 color style by "Sainnhe Park".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EVERFOREST_T16: Literal['everforest-t16'] = 'everforest-t16'
    """
    Everforest: Base-16 color style by "Sainnhe Park".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    FLAT_T16: Literal['flat-t16'] = 'flat-t16'
    """
    Flat: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    FRAMER_T16: Literal['framer-t16'] = 'framer-t16'
    """
    Framer: Base-16 color style by "Framer".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GIGAVOLT_T16: Literal['gigavolt-t16'] = 'gigavolt-t16'
    """
    Gigavolt: Base-16 color style by "Aidan Swope".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GITHUB_DARK_T16: Literal['github-dark-t16'] = 'github-dark-t16'
    """
    Github Dark: Base-16 color style by "Tinted Theming".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GOOGLE_DARK_T16: Literal['google-dark-t16'] = 'google-dark-t16'
    """
    Google Dark: Base-16 color style by "Seth Wright".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GOTHAM_T16: Literal['gotham-t16'] = 'gotham-t16'
    """
    Gotham: Base-16 color style by "Andrea Leopardi".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRAYSCALE_DARK_T16: Literal['grayscale-dark-t16'] = 'grayscale-dark-t16'
    """
    Grayscale Dark: Base-16 color style by "Alexandre Gavioli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GREENSCREEN_T16: Literal['greenscreen-t16'] = 'greenscreen-t16'
    """
    Green Screen: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUBER_T16: Literal['gruber-t16'] = 'gruber-t16'
    """
    Gruber: Base-16 color style by "Patel, Nimai, colors from
    www.github.com/rexim/gruber-darker-theme".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_DARK_HARD_T16: Literal['gruvbox-dark-hard-t16'] = 'gruvbox-dark-hard-t16'
    """
    Gruvbox dark, hard: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_DARK_MEDIUM_T16: Literal['gruvbox-dark-medium-t16'] = 'gruvbox-dark-medium-t16'
    """
    Gruvbox dark, medium: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_DARK_PALE_T16: Literal['gruvbox-dark-pale-t16'] = 'gruvbox-dark-pale-t16'
    """
    Gruvbox dark, pale: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_DARK_SOFT_T16: Literal['gruvbox-dark-soft-t16'] = 'gruvbox-dark-soft-t16'
    """
    Gruvbox dark, soft: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_DARK_T16: Literal['gruvbox-dark-t16'] = 'gruvbox-dark-t16'
    """
    Gruvbox dark: Base-16 color style by "Tinted Theming".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_MATERIAL_DARK_HARD_T16: Literal[
        'gruvbox-material-dark-hard-t16'] = 'gruvbox-material-dark-hard-t16'
    """
    Gruvbox Material Dark, Hard: Base-16 color style by "Mayush Kumar".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_MATERIAL_DARK_MEDIUM_T16: Literal[
        'gruvbox-material-dark-medium-t16'] = 'gruvbox-material-dark-medium-t16'
    """
    Gruvbox Material Dark, Medium: Base-16 color style by "Mayush Kumar".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_MATERIAL_DARK_SOFT_T16: Literal[
        'gruvbox-material-dark-soft-t16'] = 'gruvbox-material-dark-soft-t16'
    """
    Gruvbox Material Dark, Soft: Base-16 color style by "Mayush Kumar".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HARDCORE_T16: Literal['hardcore-t16'] = 'hardcore-t16'
    """
    Hardcore: Base-16 color style by "Chris Caller".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HARDHACKER_T16: Literal['hardhacker-t16'] = 'hardhacker-t16'
    """
    Hardhacker: Base-16 color style by "fe2-Nyxar, based on the
    https://github.com/hardhackerlabs".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HARMONIC16_DARK_T16: Literal['harmonic16-dark-t16'] = 'harmonic16-dark-t16'
    """
    Harmonic16 Dark: Base-16 color style by "Jannik Siebert".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HEETCH_T16: Literal['heetch-t16'] = 'heetch-t16'
    """
    Heetch Dark: Base-16 color style by "Geoffrey Teale".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HELIOS_T16: Literal['helios-t16'] = 'helios-t16'
    """
    Helios: Base-16 color style by "Alex Meyer".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HOPSCOTCH_T16: Literal['hopscotch-t16'] = 'hopscotch-t16'
    """
    Hopscotch: Base-16 color style by "Jan T. Sott".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HORIZON_DARK_T16: Literal['horizon-dark-t16'] = 'horizon-dark-t16'
    """
    Horizon Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HORIZON_TERMINAL_DARK_T16: Literal['horizon-terminal-dark-t16'] = 'horizon-terminal-dark-t16'
    """
    Horizon Terminal Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HUMANOID_DARK_T16: Literal['humanoid-dark-t16'] = 'humanoid-dark-t16'
    """
    Humanoid dark: Base-16 color style by "Thomas Friese".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    IA_DARK_T16: Literal['ia-dark-t16'] = 'ia-dark-t16'
    """
    iA Dark: Base-16 color style by "iA Inc.".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    IRBLACK_T16: Literal['irblack-t16'] = 'irblack-t16'
    """
    IR Black: Base-16 color style by "Timothée Poisot".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ISOTOPE_T16: Literal['isotope-t16'] = 'isotope-t16'
    """
    Isotope: Base-16 color style by "Jan T. Sott".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    JABUTI_T16: Literal['jabuti-t16'] = 'jabuti-t16'
    """
    Jabuti: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    KANAGAWA_DRAGON_T16: Literal['kanagawa-dragon-t16'] = 'kanagawa-dragon-t16'
    """
    Kanagawa Dragon: Base-16 color style by "Tommaso Laurenzi".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    KANAGAWA_T16: Literal['kanagawa-t16'] = 'kanagawa-t16'
    """
    Kanagawa: Base-16 color style by "Tommaso Laurenzi".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    KATY_T16: Literal['katy-t16'] = 'katy-t16'
    """
    Katy: Base-16 color style by "George Essig".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    KIMBER_T16: Literal['kimber-t16'] = 'kimber-t16'
    """
    Kimber: Base-16 color style by "Mishka Nguyen".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    LINUX_VT_T16: Literal['linux-vt-t16'] = 'linux-vt-t16'
    """
    Linux VT: Base-16 color style by "j-c-m".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MACINTOSH_T16: Literal['macintosh-t16'] = 'macintosh-t16'
    """
    Macintosh: Base-16 color style by "Rebecca Bettencourt".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MARRAKESH_T16: Literal['marrakesh-t16'] = 'marrakesh-t16'
    """
    Marrakesh: Base-16 color style by "Alexandre Gavioli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MATERIA_T16: Literal['materia-t16'] = 'materia-t16'
    """
    Materia: Base-16 color style by "Defman21".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MATERIAL_DARKER_T16: Literal['material-darker-t16'] = 'material-darker-t16'
    """
    Material Darker: Base-16 color style by "Nate Peterson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MATERIAL_PALENIGHT_T16: Literal['material-palenight-t16'] = 'material-palenight-t16'
    """
    Material Palenight: Base-16 color style by "Nate Peterson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MATERIAL_T16: Literal['material-t16'] = 'material-t16'
    """
    Material: Base-16 color style by "Nate Peterson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MEASURED_DARK_T16: Literal['measured-dark-t16'] = 'measured-dark-t16'
    """
    Measured Dark: Base-16 color style by "Measured".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MELLOW_PURPLE_T16: Literal['mellow-purple-t16'] = 'mellow-purple-t16'
    """
    Mellow Purple: Base-16 color style by "gidsi".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MOCHA_T16: Literal['mocha-t16'] = 'mocha-t16'
    """
    Mocha: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MONOKAI_T16: Literal['monokai-t16'] = 'monokai-t16'
    """
    Monokai: Base-16 color style by "Wimer Hazenberg".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MOONLIGHT_T16: Literal['moonlight-t16'] = 'moonlight-t16'
    """
    Moonlight: Base-16 color style by "Jeremy Swinarton".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MOUNTAIN_T16: Literal['mountain-t16'] = 'mountain-t16'
    """
    Mountain: Base-16 color style by "gnsfujiwara".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    NEBULA_T16: Literal['nebula-t16'] = 'nebula-t16'
    """
    Nebula: Base-16 color style by "Gabriel Fontes".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    NORD_T16: Literal['nord-t16'] = 'nord-t16'
    """
    Nord: Base-16 color style by "arcticicestudio".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    NOVA_T16: Literal['nova-t16'] = 'nova-t16'
    """
    Nova: Base-16 color style by "George Essig".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    OCEAN_T16: Literal['ocean-t16'] = 'ocean-t16'
    """
    Ocean: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    OCEANICNEXT_T16: Literal['oceanicnext-t16'] = 'oceanicnext-t16'
    """
    OceanicNext: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ONEDARK_DARK_T16: Literal['onedark-dark-t16'] = 'onedark-dark-t16'
    """
    OneDark Dark: Base-16 color style by "olimorris".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ONEDARK_T16: Literal['onedark-t16'] = 'onedark-t16'
    """
    OneDark: Base-16 color style by "Lalit Magant".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    OUTRUN_DARK_T16: Literal['outrun-dark-t16'] = 'outrun-dark-t16'
    """
    Outrun Dark: Base-16 color style by "Hugo Delahousse".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    OXOCARBON_DARK_T16: Literal['oxocarbon-dark-t16'] = 'oxocarbon-dark-t16'
    """
    Oxocarbon Dark: Base-16 color style by "shaunsingh/IBM".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PANDORA_T16: Literal['pandora-t16'] = 'pandora-t16'
    """
    pandora: Base-16 color style by "Cassandra Fox".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PARAISO_T16: Literal['paraiso-t16'] = 'paraiso-t16'
    """
    Paraiso: Base-16 color style by "Jan T. Sott".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PASQUE_T16: Literal['pasque-t16'] = 'pasque-t16'
    """
    Pasque: Base-16 color style by "Gabriel Fontes".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PENUMBRA_DARK_CONTRAST_PLUS_PLUS_T16: Literal[
        'penumbra-dark-contrast-plus-plus-t16'] = 'penumbra-dark-contrast-plus-plus-t16'
    """
    Penumbra Dark Contrast Plus Plus: Base-16 color style by "Zachary
    Weiss".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PENUMBRA_DARK_CONTRAST_PLUS_T16: Literal[
        'penumbra-dark-contrast-plus-t16'] = 'penumbra-dark-contrast-plus-t16'
    """
    Penumbra Dark Contrast Plus: Base-16 color style by "Zachary Weiss".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PENUMBRA_DARK_T16: Literal['penumbra-dark-t16'] = 'penumbra-dark-t16'
    """
    Penumbra Dark: Base-16 color style by "Zachary Weiss".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PHD_T16: Literal['phd-t16'] = 'phd-t16'
    """
    PhD: Base-16 color style by "Hennig Hasemann".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PINKY_T16: Literal['pinky-t16'] = 'pinky-t16'
    """
    pinky: Base-16 color style by "Benjamin".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    POP_T16: Literal['pop-t16'] = 'pop-t16'
    """
    Pop: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PORPLE_T16: Literal['porple-t16'] = 'porple-t16'
    """
    Porple: Base-16 color style by "Niek den Breeje".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRECIOUS_DARK_ELEVEN_T16: Literal['precious-dark-eleven-t16'] = 'precious-dark-eleven-t16'
    """
    Precious Dark Eleven: Base-16 color style by "4lex4".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRECIOUS_DARK_FIFTEEN_T16: Literal['precious-dark-fifteen-t16'] = 'precious-dark-fifteen-t16'
    """
    Precious Dark Fifteen: Base-16 color style by "4lex4".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRIMER_DARK_DIMMED_T16: Literal['primer-dark-dimmed-t16'] = 'primer-dark-dimmed-t16'
    """
    Primer Dark Dimmed: Base-16 color style by "Jimmy Lin".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRIMER_DARK_T16: Literal['primer-dark-t16'] = 'primer-dark-t16'
    """
    Primer Dark: Base-16 color style by "Jimmy Lin".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PURPLEDREAM_T16: Literal['purpledream-t16'] = 'purpledream-t16'
    """
    Purpledream: Base-16 color style by "malet".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    QUALIA_T16: Literal['qualia-t16'] = 'qualia-t16'
    """
    Qualia: Base-16 color style by "isaacwhanson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    RAILSCASTS_T16: Literal['railscasts-t16'] = 'railscasts-t16'
    """
    Railscasts: Base-16 color style by "Ryan Bates".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    REBECCA_T16: Literal['rebecca-t16'] = 'rebecca-t16'
    """
    Rebecca: Base-16 color style by "Victor Borja".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ROSE_PINE_MOON_T16: Literal['rose-pine-moon-t16'] = 'rose-pine-moon-t16'
    """
    Rosé Pine Moon: Base-16 color style by "Emilia Dunfelt".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ROSE_PINE_T16: Literal['rose-pine-t16'] = 'rose-pine-t16'
    """
    Rosé Pine: Base-16 color style by "Emilia Dunfelt".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SAGA_T16: Literal['saga-t16'] = 'saga-t16'
    """
    SAGA: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SANDCASTLE_T16: Literal['sandcastle-t16'] = 'sandcastle-t16'
    """
    Sandcastle: Base-16 color style by "George Essig".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SELENIZED_BLACK_T16: Literal['selenized-black-t16'] = 'selenized-black-t16'
    """
    selenized-black: Base-16 color style by "Jan Warchol / adapted to base16
    by ali".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SELENIZED_DARK_T16: Literal['selenized-dark-t16'] = 'selenized-dark-t16'
    """
    selenized-dark: Base-16 color style by "Jan Warchol / adapted to base16
    by ali".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SETI_T16: Literal['seti-t16'] = 'seti-t16'
    """
    Seti UI: Base-16 color style by "".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SHADES_OF_PURPLE_T16: Literal['shades-of-purple-t16'] = 'shades-of-purple-t16'
    """
    Shades of Purple: Base-16 color style by "Iolar Demartini Junior".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SHADESMEAR_DARK_T16: Literal['shadesmear-dark-t16'] = 'shadesmear-dark-t16'
    """
    ShadeSmear Dark: Base-16 color style by "Kyle Giammarco".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SILK_DARK_T16: Literal['silk-dark-t16'] = 'silk-dark-t16'
    """
    Silk Dark: Base-16 color style by "Gabriel Fontes".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SNAZZY_T16: Literal['snazzy-t16'] = 'snazzy-t16'
    """
    Snazzy: Base-16 color style by "Chawye Hsu".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SOLARFLARE_T16: Literal['solarflare-t16'] = 'solarflare-t16'
    """
    Solar Flare: Base-16 color style by "Chuck Harmston".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SOLARIZED_DARK_T16: Literal['solarized-dark-t16'] = 'solarized-dark-t16'
    """
    Solarized Dark: Base-16 color style by "Ethan Schoonover".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SPACEDUCK_T16: Literal['spaceduck-t16'] = 'spaceduck-t16'
    """
    Spaceduck: Base-16 color style by "Guillermo Rodriguez".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SPACEMACS_T16: Literal['spacemacs-t16'] = 'spacemacs-t16'
    """
    Spacemacs: Base-16 color style by "Nasser Alshammari".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SPARKY_T16: Literal['sparky-t16'] = 'sparky-t16'
    """
    Sparky: Base-16 color style by "Leila Sother".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    STANDARDIZED_DARK_T16: Literal['standardized-dark-t16'] = 'standardized-dark-t16'
    """
    standardized-dark: Base-16 color style by "ali".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    STELLA_T16: Literal['stella-t16'] = 'stella-t16'
    """
    Stella: Base-16 color style by "Shrimpram".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SUMMERFRUIT_DARK_T16: Literal['summerfruit-dark-t16'] = 'summerfruit-dark-t16'
    """
    Summerfruit Dark: Base-16 color style by "Christopher Corley".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SYNTH_MIDNIGHT_DARK_T16: Literal['synth-midnight-dark-t16'] = 'synth-midnight-dark-t16'
    """
    Synth Midnight Terminal Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TANGO_T16: Literal['tango-t16'] = 'tango-t16'
    """
    Tango: Base-16 color style by "@Schnouki, based on the Tango Desktop
    Project".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TENDER_T16: Literal['tender-t16'] = 'tender-t16'
    """
    tender: Base-16 color style by "Jacobo Tabernero".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TERRACOTTA_DARK_T16: Literal['terracotta-dark-t16'] = 'terracotta-dark-t16'
    """
    Terracotta Dark: Base-16 color style by "Alexander Rossell Hayes".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_CITY_DARK_T16: Literal['tokyo-city-dark-t16'] = 'tokyo-city-dark-t16'
    """
    Tokyo City Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_CITY_TERMINAL_DARK_T16: Literal[
        'tokyo-city-terminal-dark-t16'] = 'tokyo-city-terminal-dark-t16'
    """
    Tokyo City Terminal Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_DARK_T16: Literal['tokyo-night-dark-t16'] = 'tokyo-night-dark-t16'
    """
    Tokyo Night Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_STORM_T16: Literal['tokyo-night-storm-t16'] = 'tokyo-night-storm-t16'
    """
    Tokyo Night Storm: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYODARK_TERMINAL_T16: Literal['tokyodark-terminal-t16'] = 'tokyodark-terminal-t16'
    """
    Tokyodark Terminal: Base-16 color style by "Tiagovla".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYODARK_T16: Literal['tokyodark-t16'] = 'tokyodark-t16'
    """
    Tokyodark: Base-16 color style by "Jamy Golden".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOMORROW_NIGHT_EIGHTIES_T16: Literal[
        'tomorrow-night-eighties-t16'] = 'tomorrow-night-eighties-t16'
    """
    Tomorrow Night Eighties: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOMORROW_NIGHT_T16: Literal['tomorrow-night-t16'] = 'tomorrow-night-t16'
    """
    Tomorrow Night: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TUBE_T16: Literal['tube-t16'] = 'tube-t16'
    """
    London Tube: Base-16 color style by "Jan T. Sott".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TWILIGHT_T16: Literal['twilight-t16'] = 'twilight-t16'
    """
    Twilight: Base-16 color style by "David Hart".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    UNIKITTY_DARK_T16: Literal['unikitty-dark-t16'] = 'unikitty-dark-t16'
    """
    Unikitty Dark: Base-16 color style by "Josh W Lewis".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    UNIKITTY_REVERSIBLE_T16: Literal['unikitty-reversible-t16'] = 'unikitty-reversible-t16'
    """
    Unikitty Reversible: Base-16 color style by "Josh W Lewis".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    UWUNICORN_T16: Literal['uwunicorn-t16'] = 'uwunicorn-t16'
    """
    UwUnicorn: Base-16 color style by "Fernando Marques".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    VALUA_T16: Literal['valua-t16'] = 'valua-t16'
    """
    Valua: Base-16 color style by "Nonetrix".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    VESPER_T16: Literal['vesper-t16'] = 'vesper-t16'
    """
    Vesper: Base-16 color style by "FormalSnake".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    VICE_T16: Literal['vice-t16'] = 'vice-t16'
    """
    vice: Base-16 color style by "Thomas Leon Highbaugh".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_10_T16: Literal['windows-10-t16'] = 'windows-10-t16'
    """
    Windows 10: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_95_T16: Literal['windows-95-t16'] = 'windows-95-t16'
    """
    Windows 95: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_HIGHCONTRAST_T16: Literal['windows-highcontrast-t16'] = 'windows-highcontrast-t16'
    """
    Windows High Contrast: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_NT_T16: Literal['windows-nt-t16'] = 'windows-nt-t16'
    """
    Windows NT: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WOODLAND_T16: Literal['woodland-t16'] = 'woodland-t16'
    """
    Woodland: Base-16 color style by "Jay Cornwall".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    XCODE_DUSK_T16: Literal['xcode-dusk-t16'] = 'xcode-dusk-t16'
    """
    XCode Dusk: Base-16 color style by "Elsa Gonsiorowski".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ZENBONES_T16: Literal['zenbones-t16'] = 'zenbones-t16'
    """
    Zenbones: Base-16 color style by "mcchrish".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ZENBURN_T16: Literal['zenburn-t16'] = 'zenburn-t16'
    """
    Zenburn: Base-16 color style by "elnawe".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    RANDOM_T16_DARK_HIGH_CONTRAST: Literal['random-t16-dark-high'] = 'random-t16-dark-high'


class DarkLowContrastTintedThemingBase16ColorStyles(LiteralEnum[str]):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='Dark, lower contrast')}

    These styles have lower-level contrast that did not meet {_COLOR_CONTRAST_TEXT}
    """
    Literals = Literal['apprentice-t16',
                       'brogrammer-t16',
                       'brushtrees-dark-t16',
                       'eris-t16',
                       'eva-dim-t16',
                       'eva-t16',
                       'everforest-dark-medium-t16',
                       'icy-t16',
                       'lime-t16',
                       'material-vivid-t16',
                       'papercolor-dark-t16',
                       'pico-t16',
                       'summercamp-t16',
                       'tarot-t16',
                       'tokyo-night-moon-t16',
                       'tokyo-night-terminal-dark-t16',
                       'tokyo-night-terminal-storm-t16',
                       'vulcan-t16',
                       'random-t16-dark-low']

    APPRENTICE_T16: Literal['apprentice-t16'] = 'apprentice-t16'
    """
    Apprentice: Base-16 color style by "romainl".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    BROGRAMMER_T16: Literal['brogrammer-t16'] = 'brogrammer-t16'
    """
    Brogrammer: Base-16 color style by "Vik Ramanujam".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    BRUSHTREES_DARK_T16: Literal['brushtrees-dark-t16'] = 'brushtrees-dark-t16'
    """
    Brush Trees Dark: Base-16 color style by "Abraham White".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    ERIS_T16: Literal['eris-t16'] = 'eris-t16'
    """
    eris: Base-16 color style by "ed".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    EVA_DIM_T16: Literal['eva-dim-t16'] = 'eva-dim-t16'
    """
    Eva Dim: Base-16 color style by "kjakapat".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    EVA_T16: Literal['eva-t16'] = 'eva-t16'
    """
    Eva: Base-16 color style by "kjakapat".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    EVERFOREST_DARK_MEDIUM_T16: Literal['everforest-dark-medium-t16'] = 'everforest-dark-medium-t16'
    """
    Everforest Dark Medium: Base-16 color style by "Sainnhe Park".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    ICY_T16: Literal['icy-t16'] = 'icy-t16'
    """
    Icy Dark: Base-16 color style by "icyphox".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    LIME_T16: Literal['lime-t16'] = 'lime-t16'
    """
    lime: Base-16 color style by "limelier".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    MATERIAL_VIVID_T16: Literal['material-vivid-t16'] = 'material-vivid-t16'
    """
    Material Vivid: Base-16 color style by "joshyrobot".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    PAPERCOLOR_DARK_T16: Literal['papercolor-dark-t16'] = 'papercolor-dark-t16'
    """
    PaperColor Dark: Base-16 color style by "Jon Leopard".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    PICO_T16: Literal['pico-t16'] = 'pico-t16'
    """
    Pico: Base-16 color style by "PICO-8".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    SUMMERCAMP_T16: Literal['summercamp-t16'] = 'summercamp-t16'
    """
    summercamp: Base-16 color style by "zoe firi".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    TAROT_T16: Literal['tarot-t16'] = 'tarot-t16'
    """
    tarot: Base-16 color style by "ed".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_MOON_T16: Literal['tokyo-night-moon-t16'] = 'tokyo-night-moon-t16'
    """
    Tokyo Night Moon: Base-16 color style by "Ólafur Bjarki Bogason".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_TERMINAL_DARK_T16: Literal[
        'tokyo-night-terminal-dark-t16'] = 'tokyo-night-terminal-dark-t16'
    """
    Tokyo Night Terminal Dark: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_TERMINAL_STORM_T16: Literal[
        'tokyo-night-terminal-storm-t16'] = 'tokyo-night-terminal-storm-t16'
    """
    Tokyo Night Terminal Storm: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    VULCAN_T16: Literal['vulcan-t16'] = 'vulcan-t16'
    """
    vulcan: Base-16 color style by "Andrey Varfolomeev".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a dark variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    RANDOM_T16_DARK_LOW_CONTRAST: Literal['random-t16-dark-low'] = 'random-t16-dark-low'


class LightHighContrastTintedThemingBase16ColorStyles(LiteralEnum[str]):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='Light, high-contrast')}

    These styles have high-level contrast that conform to {_COLOR_CONTRAST_TEXT}
    """

    Literals = Literal['atelier-cave-light-t16',
                       'atelier-dune-light-t16',
                       'atelier-estuary-light-t16',
                       'atelier-forest-light-t16',
                       'atelier-heath-light-t16',
                       'atelier-lakeside-light-t16',
                       'atelier-plateau-light-t16',
                       'atelier-savanna-light-t16',
                       'atelier-seaside-light-t16',
                       'atelier-sulphurpool-light-t16',
                       'ayu-light-t16',
                       'catppuccin-latte-t16',
                       'charcoal-light-t16',
                       'chicago-day-t16',
                       'chinoiserie-t16',
                       'classic-light-t16',
                       'cupertino-t16',
                       'da-one-paper-t16',
                       'da-one-white-t16',
                       'danqing-light-t16',
                       'default-light-t16',
                       'dirtysea-t16',
                       'edge-light-t16',
                       'embers-light-t16',
                       'emil-t16',
                       'equilibrium-gray-light-t16',
                       'equilibrium-light-t16',
                       'fruit-soda-t16',
                       'github-t16',
                       'google-light-t16',
                       'grayscale-light-t16',
                       'gruvbox-light-hard-t16',
                       'gruvbox-light-medium-t16',
                       'gruvbox-light-soft-t16',
                       'gruvbox-light-t16',
                       'gruvbox-material-light-hard-t16',
                       'gruvbox-material-light-medium-t16',
                       'gruvbox-material-light-soft-t16',
                       'harmonic16-light-t16',
                       'heetch-light-t16',
                       'horizon-light-t16',
                       'horizon-terminal-light-t16',
                       'humanoid-light-t16',
                       'ia-light-t16',
                       'measured-light-t16',
                       'mexico-light-t16',
                       'nord-light-t16',
                       'one-light-t16',
                       'oxocarbon-light-t16',
                       'papercolor-light-t16',
                       'penumbra-light-contrast-plus-plus-t16',
                       'penumbra-light-contrast-plus-t16',
                       'penumbra-light-t16',
                       'precious-light-warm-t16',
                       'precious-light-white-t16',
                       'primer-light-t16',
                       'rose-pine-dawn-t16',
                       'sagelight-t16',
                       'sakura-t16',
                       'selenized-light-t16',
                       'selenized-white-t16',
                       'shadesmear-light-t16',
                       'shapeshifter-t16',
                       'silk-light-t16',
                       'solarflare-light-t16',
                       'solarized-light-t16',
                       'standardized-light-t16',
                       'still-alive-t16',
                       'summerfruit-light-t16',
                       'synth-midnight-light-t16',
                       'terracotta-t16',
                       'tokyo-city-light-t16',
                       'tokyo-city-terminal-light-t16',
                       'tokyo-night-light-t16',
                       'tokyo-night-terminal-light-t16',
                       'tomorrow-t16',
                       'unikitty-light-t16',
                       'windows-95-light-t16',
                       'windows-highcontrast-light-t16',
                       'random-t16-light-high']

    ATELIER_CAVE_LIGHT_T16: Literal['atelier-cave-light-t16'] = 'atelier-cave-light-t16'
    """
    Atelier Cave Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_DUNE_LIGHT_T16: Literal['atelier-dune-light-t16'] = 'atelier-dune-light-t16'
    """
    Atelier Dune Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_ESTUARY_LIGHT_T16: Literal['atelier-estuary-light-t16'] = 'atelier-estuary-light-t16'
    """
    Atelier Estuary Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_FOREST_LIGHT_T16: Literal['atelier-forest-light-t16'] = 'atelier-forest-light-t16'
    """
    Atelier Forest Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_HEATH_LIGHT_T16: Literal['atelier-heath-light-t16'] = 'atelier-heath-light-t16'
    """
    Atelier Heath Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_LAKESIDE_LIGHT_T16: Literal['atelier-lakeside-light-t16'] = 'atelier-lakeside-light-t16'
    """
    Atelier Lakeside Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_PLATEAU_LIGHT_T16: Literal['atelier-plateau-light-t16'] = 'atelier-plateau-light-t16'
    """
    Atelier Plateau Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_SAVANNA_LIGHT_T16: Literal['atelier-savanna-light-t16'] = 'atelier-savanna-light-t16'
    """
    Atelier Savanna Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_SEASIDE_LIGHT_T16: Literal['atelier-seaside-light-t16'] = 'atelier-seaside-light-t16'
    """
    Atelier Seaside Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ATELIER_SULPHURPOOL_LIGHT_T16: Literal[
        'atelier-sulphurpool-light-t16'] = 'atelier-sulphurpool-light-t16'
    """
    Atelier Sulphurpool Light: Base-16 color style by "Bram de Haan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    AYU_LIGHT_T16: Literal['ayu-light-t16'] = 'ayu-light-t16'
    """
    Ayu Light: Base-16 color style by "Khue Nguyen".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CATPPUCCIN_LATTE_T16: Literal['catppuccin-latte-t16'] = 'catppuccin-latte-t16'
    """
    Catppuccin Latte: Base-16 color style.

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHARCOAL_LIGHT_T16: Literal['charcoal-light-t16'] = 'charcoal-light-t16'
    """
    Charcoal Light: Base-16 color style by "Mubin Muhammad".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHICAGO_DAY_T16: Literal['chicago-day-t16'] = 'chicago-day-t16'
    """
    Chicago Day: Base-16 color style by "Wendell, Ryan".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CHINOISERIE_T16: Literal['chinoiserie-t16'] = 'chinoiserie-t16'
    """
    Chinoiserie: Base-16 color style by "Di Wang".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CLASSIC_LIGHT_T16: Literal['classic-light-t16'] = 'classic-light-t16'
    """
    Classic Light: Base-16 color style by "Jason Heeris".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    CUPERTINO_T16: Literal['cupertino-t16'] = 'cupertino-t16'
    """
    Cupertino: Base-16 color style by "Defman21".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DA_ONE_PAPER_T16: Literal['da-one-paper-t16'] = 'da-one-paper-t16'
    """
    Da One Paper: Base-16 color style by "NNB".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DA_ONE_WHITE_T16: Literal['da-one-white-t16'] = 'da-one-white-t16'
    """
    Da One White: Base-16 color style by "NNB".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DANQING_LIGHT_T16: Literal['danqing-light-t16'] = 'danqing-light-t16'
    """
    DanQing Light: Base-16 color style by "Wenhan Zhu".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DEFAULT_LIGHT_T16: Literal['default-light-t16'] = 'default-light-t16'
    """
    Default Light: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    DIRTYSEA_T16: Literal['dirtysea-t16'] = 'dirtysea-t16'
    """
    dirtysea: Base-16 color style by "Kahlil Hodgson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EDGE_LIGHT_T16: Literal['edge-light-t16'] = 'edge-light-t16'
    """
    Edge Light: Base-16 color style by "cjayross".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EMBERS_LIGHT_T16: Literal['embers-light-t16'] = 'embers-light-t16'
    """
    Embers Light: Base-16 color style by "Jannik Siebert".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EMIL_T16: Literal['emil-t16'] = 'emil-t16'
    """
    emil: Base-16 color style by "limelier".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EQUILIBRIUM_GRAY_LIGHT_T16: Literal['equilibrium-gray-light-t16'] = 'equilibrium-gray-light-t16'
    """
    Equilibrium Gray Light: Base-16 color style by "Carlo Abelli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    EQUILIBRIUM_LIGHT_T16: Literal['equilibrium-light-t16'] = 'equilibrium-light-t16'
    """
    Equilibrium Light: Base-16 color style by "Carlo Abelli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    FRUIT_SODA_T16: Literal['fruit-soda-t16'] = 'fruit-soda-t16'
    """
    Fruit Soda: Base-16 color style by "jozip".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GITHUB_T16: Literal['github-t16'] = 'github-t16'
    """
    Github: Base-16 color style by "Tinted Theming".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GOOGLE_LIGHT_T16: Literal['google-light-t16'] = 'google-light-t16'
    """
    Google Light: Base-16 color style by "Seth Wright".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRAYSCALE_LIGHT_T16: Literal['grayscale-light-t16'] = 'grayscale-light-t16'
    """
    Grayscale Light: Base-16 color style by "Alexandre Gavioli".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_LIGHT_HARD_T16: Literal['gruvbox-light-hard-t16'] = 'gruvbox-light-hard-t16'
    """
    Gruvbox light, hard: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_LIGHT_MEDIUM_T16: Literal['gruvbox-light-medium-t16'] = 'gruvbox-light-medium-t16'
    """
    Gruvbox light, medium: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_LIGHT_SOFT_T16: Literal['gruvbox-light-soft-t16'] = 'gruvbox-light-soft-t16'
    """
    Gruvbox light, soft: Base-16 color style by "Dawid Kurek".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_LIGHT_T16: Literal['gruvbox-light-t16'] = 'gruvbox-light-t16'
    """
    Gruvbox Light: Base-16 color style by "Tinted Theming".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_MATERIAL_LIGHT_HARD_T16: Literal[
        'gruvbox-material-light-hard-t16'] = 'gruvbox-material-light-hard-t16'
    """
    Gruvbox Material Light, Hard: Base-16 color style by "Mayush Kumar".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_MATERIAL_LIGHT_MEDIUM_T16: Literal[
        'gruvbox-material-light-medium-t16'] = 'gruvbox-material-light-medium-t16'
    """
    Gruvbox Material Light, Medium: Base-16 color style by "Mayush Kumar".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    GRUVBOX_MATERIAL_LIGHT_SOFT_T16: Literal[
        'gruvbox-material-light-soft-t16'] = 'gruvbox-material-light-soft-t16'
    """
    Gruvbox Material Light, Soft: Base-16 color style by "Mayush Kumar".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HARMONIC16_LIGHT_T16: Literal['harmonic16-light-t16'] = 'harmonic16-light-t16'
    """
    Harmonic16 Light: Base-16 color style by "Jannik Siebert".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HEETCH_LIGHT_T16: Literal['heetch-light-t16'] = 'heetch-light-t16'
    """
    Heetch Light: Base-16 color style by "Geoffrey Teale".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HORIZON_LIGHT_T16: Literal['horizon-light-t16'] = 'horizon-light-t16'
    """
    Horizon Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HORIZON_TERMINAL_LIGHT_T16: Literal['horizon-terminal-light-t16'] = 'horizon-terminal-light-t16'
    """
    Horizon Terminal Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    HUMANOID_LIGHT_T16: Literal['humanoid-light-t16'] = 'humanoid-light-t16'
    """
    Humanoid light: Base-16 color style by "Thomas Friese".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    IA_LIGHT_T16: Literal['ia-light-t16'] = 'ia-light-t16'
    """
    iA Light: Base-16 color style by "iA Inc.".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MEASURED_LIGHT_T16: Literal['measured-light-t16'] = 'measured-light-t16'
    """
    Measured Light: Base-16 color style by "Measured".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    MEXICO_LIGHT_T16: Literal['mexico-light-t16'] = 'mexico-light-t16'
    """
    Mexico Light: Base-16 color style by "Sheldon Johnson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    NORD_LIGHT_T16: Literal['nord-light-t16'] = 'nord-light-t16'
    """
    Nord Light: Base-16 color style by "threddast, based on fuxialexander's
    doom-nord-light-theme".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ONE_LIGHT_T16: Literal['one-light-t16'] = 'one-light-t16'
    """
    One Light: Base-16 color style by "Daniel Pfeifer".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    OXOCARBON_LIGHT_T16: Literal['oxocarbon-light-t16'] = 'oxocarbon-light-t16'
    """
    Oxocarbon Light: Base-16 color style by "shaunsingh/IBM".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PAPERCOLOR_LIGHT_T16: Literal['papercolor-light-t16'] = 'papercolor-light-t16'
    """
    PaperColor Light: Base-16 color style by "Jon Leopard".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PENUMBRA_LIGHT_CONTRAST_PLUS_PLUS_T16: Literal[
        'penumbra-light-contrast-plus-plus-t16'] = 'penumbra-light-contrast-plus-plus-t16'
    """
    Penumbra Light Contrast Plus Plus: Base-16 color style by "Zachary
    Weiss".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PENUMBRA_LIGHT_CONTRAST_PLUS_T16: Literal[
        'penumbra-light-contrast-plus-t16'] = 'penumbra-light-contrast-plus-t16'
    """
    Penumbra Light Contrast Plus: Base-16 color style by "Zachary Weiss".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PENUMBRA_LIGHT_T16: Literal['penumbra-light-t16'] = 'penumbra-light-t16'
    """
    Penumbra Light: Base-16 color style by "Zachary Weiss".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRECIOUS_LIGHT_WARM_T16: Literal['precious-light-warm-t16'] = 'precious-light-warm-t16'
    """
    Precious Light Warm: Base-16 color style by "4lex4".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRECIOUS_LIGHT_WHITE_T16: Literal['precious-light-white-t16'] = 'precious-light-white-t16'
    """
    Precious Light White: Base-16 color style by "4lex4".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    PRIMER_LIGHT_T16: Literal['primer-light-t16'] = 'primer-light-t16'
    """
    Primer Light: Base-16 color style by "Jimmy Lin".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    ROSE_PINE_DAWN_T16: Literal['rose-pine-dawn-t16'] = 'rose-pine-dawn-t16'
    """
    Rosé Pine Dawn: Base-16 color style by "Emilia Dunfelt".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SAGELIGHT_T16: Literal['sagelight-t16'] = 'sagelight-t16'
    """
    Sagelight: Base-16 color style by "Carter Veldhuizen".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SAKURA_T16: Literal['sakura-t16'] = 'sakura-t16'
    """
    Sakura: Base-16 color style by "Misterio77".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SELENIZED_LIGHT_T16: Literal['selenized-light-t16'] = 'selenized-light-t16'
    """
    selenized-light: Base-16 color style by "Jan Warchol / adapted to base16
    by ali".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SELENIZED_WHITE_T16: Literal['selenized-white-t16'] = 'selenized-white-t16'
    """
    selenized-white: Base-16 color style by "Jan Warchol / adapted to base16
    by ali".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SHADESMEAR_LIGHT_T16: Literal['shadesmear-light-t16'] = 'shadesmear-light-t16'
    """
    ShadeSmear Light: Base-16 color style by "Kyle Giammarco".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SHAPESHIFTER_T16: Literal['shapeshifter-t16'] = 'shapeshifter-t16'
    """
    Shapeshifter: Base-16 color style by "Tyler Benziger".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SILK_LIGHT_T16: Literal['silk-light-t16'] = 'silk-light-t16'
    """
    Silk Light: Base-16 color style by "Gabriel Fontes".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SOLARFLARE_LIGHT_T16: Literal['solarflare-light-t16'] = 'solarflare-light-t16'
    """
    Solar Flare Light: Base-16 color style by "Chuck Harmston".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SOLARIZED_LIGHT_T16: Literal['solarized-light-t16'] = 'solarized-light-t16'
    """
    Solarized Light: Base-16 color style by "Ethan Schoonover".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    STANDARDIZED_LIGHT_T16: Literal['standardized-light-t16'] = 'standardized-light-t16'
    """
    standardized-light: Base-16 color style by "ali".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    STILL_ALIVE_T16: Literal['still-alive-t16'] = 'still-alive-t16'
    """
    Still Alive: Base-16 color style by "Derrick McKee".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SUMMERFRUIT_LIGHT_T16: Literal['summerfruit-light-t16'] = 'summerfruit-light-t16'
    """
    Summerfruit Light: Base-16 color style by "Christopher Corley".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    SYNTH_MIDNIGHT_LIGHT_T16: Literal['synth-midnight-light-t16'] = 'synth-midnight-light-t16'
    """
    Synth Midnight Terminal Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TERRACOTTA_T16: Literal['terracotta-t16'] = 'terracotta-t16'
    """
    Terracotta: Base-16 color style by "Alexander Rossell Hayes".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_CITY_LIGHT_T16: Literal['tokyo-city-light-t16'] = 'tokyo-city-light-t16'
    """
    Tokyo City Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_CITY_TERMINAL_LIGHT_T16: Literal[
        'tokyo-city-terminal-light-t16'] = 'tokyo-city-terminal-light-t16'
    """
    Tokyo City Terminal Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_LIGHT_T16: Literal['tokyo-night-light-t16'] = 'tokyo-night-light-t16'
    """
    Tokyo Night Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOKYO_NIGHT_TERMINAL_LIGHT_T16: Literal[
        'tokyo-night-terminal-light-t16'] = 'tokyo-night-terminal-light-t16'
    """
    Tokyo Night Terminal Light: Base-16 color style by "Michaël Ball".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    TOMORROW_T16: Literal['tomorrow-t16'] = 'tomorrow-t16'
    """
    Tomorrow: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    UNIKITTY_LIGHT_T16: Literal['unikitty-light-t16'] = 'unikitty-light-t16'
    """
    Unikitty Light: Base-16 color style by "Josh W Lewis".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_95_LIGHT_T16: Literal['windows-95-light-t16'] = 'windows-95-light-t16'
    """
    Windows 95 Light: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_HIGHCONTRAST_LIGHT_T16: Literal[
        'windows-highcontrast-light-t16'] = 'windows-highcontrast-light-t16'
    """
    Windows High Contrast Light: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with high-level contrast that conforms to
    the AA criteria of the Web Content Accessibility Guidelines (WCAG) 2.1
    (https://www.w3.org/TR/WCAG21/).
    """

    RANDOM_T16_LIGHT_HIGH_CONTRAST: Literal['random-t16-light-high'] = 'random-t16-light-high'


class LightLowContrastTintedThemingBase16ColorStyles(LiteralEnum[str]):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='Light, lower contrast')}

    These styles have lower-level contrast that did not meet {_COLOR_CONTRAST_TEXT}
    """

    Literals = Literal['brushtrees-t16',
                       'cupcake-t16',
                       'material-lighter-t16',
                       'windows-10-light-t16',
                       'windows-nt-light-t16',
                       'random-t16-light-low']

    BRUSHTREES_T16: Literal['brushtrees-t16'] = 'brushtrees-t16'
    """
    Brush Trees: Base-16 color style by "Abraham White".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    CUPCAKE_T16: Literal['cupcake-t16'] = 'cupcake-t16'
    """
    Cupcake: Base-16 color style by "Chris Kempson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    MATERIAL_LIGHTER_T16: Literal['material-lighter-t16'] = 'material-lighter-t16'
    """
    Material Lighter: Base-16 color style by "Nate Peterson".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_10_LIGHT_T16: Literal['windows-10-light-t16'] = 'windows-10-light-t16'
    """
    Windows 10 Light: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    WINDOWS_NT_LIGHT_T16: Literal['windows-nt-light-t16'] = 'windows-nt-light-t16'
    """
    Windows NT Light: Base-16 color style by "Fergus Collins".

    Collected by Tinted Theming (https://github.com/tinted-theming/schemes).
    Automatically downloaded by Omnipy when needed (locally cached).

    This style is a light variant, with lower-level contrast that did not
    meet the AA criteria of the Web Content Accessibility Guidelines (WCAG)
    2.1 (https://www.w3.org/TR/WCAG21/).
    """

    RANDOM_T16_LIGHT_LOW_CONTRAST: Literal['random-t16-light-low'] = 'random-t16-light-low'


class DarkTintedThemingBase16ColorStyles(
        DarkHighContrastTintedThemingBase16ColorStyles,
        DarkLowContrastTintedThemingBase16ColorStyles,
):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='All dark')}
    """

    Literals = Literal[DarkHighContrastTintedThemingBase16ColorStyles.Literals,
                       DarkLowContrastTintedThemingBase16ColorStyles.Literals,
                       'random-t16-dark']

    RANDOM_T16_DARK: Literal['random-t16-dark'] = 'random-t16-dark'


class LightTintedThemingBase16ColorStyles(
        LightHighContrastTintedThemingBase16ColorStyles,
        LightLowContrastTintedThemingBase16ColorStyles,
):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='All light')}
    """

    Literals = Literal[LightHighContrastTintedThemingBase16ColorStyles.Literals,
                       LightLowContrastTintedThemingBase16ColorStyles.Literals,
                       'random-t16-light']

    RANDOM_T16_LIGHT: Literal['random-t16-light'] = 'random-t16-light'


class TintedThemingBase16ColorStyles(
        DarkTintedThemingBase16ColorStyles,
        LightTintedThemingBase16ColorStyles,
):
    f"""
    {_GENERAL_T16_COLOR_STYLE_DOCSTRING.format(description='All')}
    """

    Literals = Literal[DarkTintedThemingBase16ColorStyles.Literals,
                       LightTintedThemingBase16ColorStyles.Literals,
                       'random-t16']

    RANDOM_T16: Literal['random-t16'] = 'random-t16'


_GENERAL_PYGMENTS_COLOR_STYLE_DOCSTRING = dedent("""
    provided by the Pygments library. See
    the Pygment docs for an overview of all Pygment-included styles:
    https://pygments.org/styles/
    """)


class DarkHighContrastPygmentsColorStyles(LiteralEnum[str]):
    __doc__ = (
        dedent("""
        High contrast dark color styles for syntax highlighting, """)
        + _GENERAL_PYGMENTS_COLOR_STYLE_DOCSTRING)

    Literals = Literal[
        'github-dark-pygments',
        'lightbulb-pygments',
        'monokai-pygments',
        'rrt-pygments',
    ]

    GITHUB_DARK_PYGMENTS: Literal['github-dark-pygments'] = 'github-dark-pygments'
    LIGHTBULB_PYGMENTS: Literal['lightbulb-pygments'] = 'lightbulb-pygments'
    MONOKAI_PYGMENTS: Literal['monokai-pygments'] = 'monokai-pygments'
    RRT_PYGMENTS: Literal['rrt-pygments'] = 'rrt-pygments'


class DarkLowContrastPygmentsColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        Lower contrast dark color styles for syntax highlighting.
        """) + _GENERAL_PYGMENTS_COLOR_STYLE_DOCSTRING

    Literals = Literal[
        'coffee-pygments',
        'dracula-pygments',
        'fruity-pygments',
        'gruvbox-dark-pygments',
        'inkpot-pygments',
        'material-pygments',
        'native-pygments',
        'nord-darker-pygments',
        'nord-pygments',
        'one-dark-pygments',
        'paraiso-dark-pygments',
        'solarized-dark-pygments',
        'stata-dark-pygments',
        'vim-pygments',
        'zenburn-pygments',
    ]

    COFFEE_PYGMENTS: Literal['coffee-pygments'] = 'coffee-pygments'
    DRACULA_PYGMENTS: Literal['dracula-pygments'] = 'dracula-pygments'
    FRUITY_PYGMENTS: Literal['fruity-pygments'] = 'fruity-pygments'
    GRUVBOX_DARK_PYGMENTS: Literal['gruvbox-dark-pygments'] = 'gruvbox-dark-pygments'
    INKPOT_PYGMENTS: Literal['inkpot-pygments'] = 'inkpot-pygments'
    MATERIAL_PYGMENTS: Literal['material-pygments'] = 'material-pygments'
    NATIVE_PYGMENTS: Literal['native-pygments'] = 'native-pygments'
    NORD_DARKER_PYGMENTS: Literal['nord-darker-pygments'] = 'nord-darker-pygments'
    NORD_PYGMENTS: Literal['nord-pygments'] = 'nord-pygments'
    ONE_DARK_PYGMENTS: Literal['one-dark-pygments'] = 'one-dark-pygments'
    PARAISO_DARK_PYGMENTS: Literal['paraiso-dark-pygments'] = 'paraiso-dark-pygments'
    SOLARIZED_DARK_PYGMENTS: Literal['solarized-dark-pygments'] = 'solarized-dark-pygments'
    STATA_DARK_PYGMENTS: Literal['stata-dark-pygments'] = 'stata-dark-pygments'
    VIM_PYGMENTS: Literal['vim-pygments'] = 'vim-pygments'
    ZENBURN_PYGMENTS: Literal['zenburn-pygments'] = 'zenburn-pygments'


class LightHighContrastPygmentsColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        High contrast light color styles for syntax highlighting.
        """) + _GENERAL_PYGMENTS_COLOR_STYLE_DOCSTRING

    Literals = Literal[
        'bw-pygments',
        'default-pygments',
        'sas-pygments',
        'staroffice-pygments',
        'xcode-pygments',
    ]

    BW_PYGMENTS: Literal['bw-pygments'] = 'bw-pygments'
    DEFAULT_PYGMENTS: Literal['default-pygments'] = 'default-pygments'
    SAS_PYGMENTS: Literal['sas-pygments'] = 'sas-pygments'
    STAROFFICE_PYGMENTS: Literal['staroffice-pygments'] = 'staroffice-pygments'
    XCODE_PYGMENTS: Literal['xcode-pygments'] = 'xcode-pygments'


class LightLowContrastPygmentsColorStyles(LiteralEnum[str]):
    __doc__ = dedent("""
        Lower contrast dark color styles for syntax highlighting.
        """) + _GENERAL_PYGMENTS_COLOR_STYLE_DOCSTRING

    Literals = Literal[
        'abap-pygments',
        'algol-pygments',
        'algol_nu-pygments',
        'arduino-pygments',
        'autumn-pygments',
        'borland-pygments',
        'colorful-pygments',
        'emacs-pygments',
        'friendly_grayscale-pygments',
        'friendly-pygments',
        'gruvbox-light-pygments',
        'igor-pygments',
        'lovelace-pygments',
        'manni-pygments',
        'murphy-pygments',
        'paraiso-light-pygments',
        'pastie-pygments',
        'perldoc-pygments',
        'rainbow_dash-pygments',
        'solarized-light-pygments',
        'stata-light-pygments',
        'tango-pygments',
        'trac-pygments',
        'vs-pygments',
    ]

    ABAP_PYGMENTS: Literal['abap-pygments'] = 'abap-pygments'
    ALGOL_PYGMENTS: Literal['algol-pygments'] = 'algol-pygments'
    ALGOL_NU_PYGMENTS: Literal['algol_nu-pygments'] = 'algol_nu-pygments'
    ARDUINO_PYGMENTS: Literal['arduino-pygments'] = 'arduino-pygments'
    AUTUMN_PYGMENTS: Literal['autumn-pygments'] = 'autumn-pygments'
    BORLAND_PYGMENTS: Literal['borland-pygments'] = 'borland-pygments'
    COLORFUL_PYGMENTS: Literal['colorful-pygments'] = 'colorful-pygments'
    EMACS_PYGMENTS: Literal['emacs-pygments'] = 'emacs-pygments'
    FRIENDLY_GRAYSCALE_PYGMENTS: Literal[
        'friendly_grayscale-pygments'] = 'friendly_grayscale-pygments'
    FRIENDLY_PYGMENTS: Literal['friendly-pygments'] = 'friendly-pygments'
    GRUVBOX_LIGHT_PYGMENTS: Literal['gruvbox-light-pygments'] = 'gruvbox-light-pygments'
    IGOR_PYGMENTS: Literal['igor-pygments'] = 'igor-pygments'
    LOVELACE_PYGMENTS: Literal['lovelace-pygments'] = 'lovelace-pygments'
    MANNI_PYGMENTS: Literal['manni-pygments'] = 'manni-pygments'
    MURPHY_PYGMENTS: Literal['murphy-pygments'] = 'murphy-pygments'
    PARAISO_LIGHT_PYGMENTS: Literal['paraiso-light-pygments'] = 'paraiso-light-pygments'
    PASTIE_PYGMENTS: Literal['pastie-pygments'] = 'pastie-pygments'
    PERLDOC_PYGMENTS: Literal['perldoc-pygments'] = 'perldoc-pygments'
    RAINBOW_DASH_PYGMENTS: Literal['rainbow_dash-pygments'] = 'rainbow_dash-pygments'
    SOLARIZED_LIGHT_PYGMENTS: Literal['solarized-light-pygments'] = 'solarized-light-pygments'
    STATA_LIGHT_PYGMENTS: Literal['stata-light-pygments'] = 'stata-light-pygments'
    TANGO_PYGMENTS: Literal['tango-pygments'] = 'tango-pygments'
    TRAC_PYGMENTS: Literal['trac-pygments'] = 'trac-pygments'
    VS_PYGMENTS: Literal['vs-pygments'] = 'vs-pygments'


class DarkHighContrastColorStyles(
        DarkHighContrastTintedThemingBase16ColorStyles,
        DarkHighContrastPygmentsColorStyles,
):
    """
    All dark, high contrast color styles for syntax highlighting. See
    subclasses for more details on the color styles.
    """

    Literals = Literal[DarkHighContrastTintedThemingBase16ColorStyles.Literals,
                       DarkHighContrastPygmentsColorStyles.Literals,
                       'random-dark-high']

    RANDOM_DARK_HIGH_CONTRAST: Literal['random-dark-high'] = 'random-dark-high'


class DarkLowContrastColorStyles(
        DarkLowContrastTintedThemingBase16ColorStyles,
        DarkLowContrastPygmentsColorStyles,
):
    """
    All dark, lower contrast color styles for syntax highlighting. See
    superclasses for more details on the color styles.
    """

    Literals = Literal[DarkLowContrastTintedThemingBase16ColorStyles.Literals,
                       DarkLowContrastPygmentsColorStyles.Literals,
                       'random-dark-low']

    RANDOM_DARK_LOW_CONTRAST: Literal['random-dark-low'] = 'random-dark-low'


class LightHighContrastColorStyles(
        LightHighContrastTintedThemingBase16ColorStyles,
        LightHighContrastPygmentsColorStyles,
):
    """
    All light, high contrast color styles for syntax highlighting. See
    superclasses for more details on the color styles.
    """

    Literals = Literal[LightHighContrastTintedThemingBase16ColorStyles.Literals,
                       LightHighContrastPygmentsColorStyles.Literals,
                       'random-light-high']

    RANDOM_LIGHT_HIGH_CONTRAST: Literal['random-light-high'] = 'random-light-high'


class LightLowContrastColorStyles(
        LightLowContrastTintedThemingBase16ColorStyles,
        LightLowContrastPygmentsColorStyles,
):
    """
    All light, lower contrast color styles for syntax highlighting. See
    superclasses for more details on the color styles.
    """

    Literals = Literal[LightLowContrastTintedThemingBase16ColorStyles.Literals,
                       LightLowContrastPygmentsColorStyles.Literals,
                       'random-light-low']

    RANDOM_LIGHT_LOW_CONTRAST: Literal['random-light-low'] = 'random-light-low'


class DarkColorStyles(
        DarkHighContrastColorStyles,
        DarkLowContrastColorStyles,
):
    """
    All dark color styles for syntax highlighting. See subclasses for more
    details on the color styles.
    """

    Literals = Literal[DarkHighContrastColorStyles.Literals,
                       DarkLowContrastColorStyles.Literals,
                       'random-dark']

    RANDOM_DARK: Literal['random-dark'] = 'random-dark'


class LightColorStyles(
        LightHighContrastColorStyles,
        LightLowContrastColorStyles,
):
    """
    All light color styles for syntax highlighting. See subclasses for more
    details on the color styles.
    """

    Literals = Literal[LightHighContrastColorStyles.Literals,
                       LightLowContrastColorStyles.Literals,
                       'random-light']

    RANDOM_LIGHT: Literal['random-light'] = 'random-light'


class AllColorStyles(
        RecommendedColorStyles,
        DarkColorStyles,
        LightColorStyles,
        TintedThemingBase16ColorStyles,
):
    """
    All color styles available for syntax highlighting. See superclasses for
    more details on the color styles.
    """

    Literals = Literal[RecommendedColorStyles.Literals,
                       DarkColorStyles.Literals,
                       LightColorStyles.Literals,
                       TintedThemingBase16ColorStyles.Literals,
                       'random']

    RANDOM_ALL: Literal['random'] = 'random'

    @classmethod
    def get_supercls_for_random_choice(
            cls, choice: 'AllColorStyles.Literals | str') -> type[LiteralEnum[str]] | None:
        """
        Returns the superclass that contains the given choice.
        """
        for supercls in reversed(cls.__mro__):
            if (issubclass(supercls, LiteralEnum) and supercls is not LiteralEnum
                    and choice in supercls):
                return supercls
