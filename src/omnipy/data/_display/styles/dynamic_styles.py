from functools import lru_cache
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from inflection import dasherize, underscore
import pygments.style
import pygments.styles
from ruamel.yaml import YAML

from omnipy.data._display.styles.helpers import Base16Theme, get_styles_from_base16_colors
from omnipy.shared.constants import (ANSI_PREFIX,
                                     PYGMENTS_SUFFIX,
                                     RANDOM_PREFIX,
                                     STYLE_CLS_NAME_SUFFIX,
                                     STYLE_CLS_NAME_TINTED_BASE16_PREFIX,
                                     THEME_KEY_TINTED_BASE16_SUFFIX)
from omnipy.shared.enums.colorstyles import AllColorStyles
from omnipy.shared.protocols.hub.runtime import IsRuntime

_BASE16_DOWNLOAD_URL = ('https://raw.githubusercontent.com/tinted-theming/'
                        'schemes/refs/heads/spec-0.11/base16/')
_runtime: IsRuntime | None = None


class TintedBase16Style(pygments.style.Style):
    name: str
    author: str
    variant: str


def fetch_base16_theme(theme_url: str) -> Base16Theme:
    from omnipy.hub.runtime import runtime
    if not runtime:
        assert _runtime
        runtime = _runtime

    cache_dir_path = Path(runtime.config.data.ui.cache_dir_path) / 'styles'
    if not os.path.exists(cache_dir_path):
        os.makedirs(cache_dir_path)

    theme_cache_path = cache_dir_path / os.path.basename(urlparse(theme_url).path)
    if os.path.exists(theme_cache_path):
        with open(theme_cache_path, 'rb') as f:
            base16_theme_yaml = f.read()
    else:
        with urlopen(theme_url) as response:
            base16_theme_yaml = response.read()

        with open(theme_cache_path, 'wb') as f:
            f.write(base16_theme_yaml)

    yaml = YAML(typ='safe')
    response = yaml.load(base16_theme_yaml)

    if 'system' in response and response['system'] == 'base16':
        del response['system']
        return Base16Theme(**response)

    raise ValueError('The response is not a base16 theme')


def create_dynamic_base16_style_class(
    theme_key: str,
    base16_theme: Base16Theme,
) -> type[TintedBase16Style]:
    return type(
        _create_base_16_class_name_from_theme_key(theme_key), (TintedBase16Style,),
        {
            'name': base16_theme.name,
            'author': base16_theme.author,
            'variant': base16_theme.variant,
            'background_color': base16_theme.palette.base00,
            'highlight_color': base16_theme.palette.base02,
            'styles': get_styles_from_base16_colors(base16_theme.palette),
        })


def _fetch_base16_theme_and_create_dynamic_style_class(
    theme_key: str,
    base16_url: str,
) -> type[TintedBase16Style]:
    base16_theme = fetch_base16_theme(base16_url)
    return create_dynamic_base16_style_class(theme_key, base16_theme)


def _create_base_16_class_name_from_theme_key(base16_theme_name: str):
    assert base16_theme_name.endswith(THEME_KEY_TINTED_BASE16_SUFFIX)
    base16_theme_name_stripped = base16_theme_name[:-len(THEME_KEY_TINTED_BASE16_SUFFIX)]

    class_name = (f'{STYLE_CLS_NAME_TINTED_BASE16_PREFIX}'
                  f"{_capitalize_words(underscore(base16_theme_name_stripped)).replace(' ', '')}"
                  f'{STYLE_CLS_NAME_SUFFIX}')

    return class_name


def _capitalize_words(text: str) -> str:
    return ' '.join(word.capitalize() for word in text.split())


@lru_cache
def __getattr__(attr: str) -> type[pygments.style.Style]:
    try:
        if attr.startswith(STYLE_CLS_NAME_TINTED_BASE16_PREFIX) and attr.endswith(
                STYLE_CLS_NAME_SUFFIX):
            stripped_name = \
                attr[len(STYLE_CLS_NAME_TINTED_BASE16_PREFIX):-len(STYLE_CLS_NAME_SUFFIX)]

            core_name = dasherize(underscore(stripped_name))
            filename = core_name + '.yaml'
            theme_key = core_name + THEME_KEY_TINTED_BASE16_SUFFIX

            base16_url = f'{_BASE16_DOWNLOAD_URL}/{filename}'
            return _fetch_base16_theme_and_create_dynamic_style_class(
                theme_key,
                base16_url,
            )

    except (IOError, ValueError) as e:
        raise AttributeError(f'Failed to fetch base16 theme: {e}') from e

    raise AttributeError(f"Module '{__name__}' has no attribute '{attr}'")


def handle_random_name(name: str | AllColorStyles.Literals) -> str:
    if name.startswith(RANDOM_PREFIX):
        color_style_cls = AllColorStyles.get_supercls_for_random_choice(name)
        if color_style_cls:
            return color_style_cls.random_choice()
        else:
            raise ValueError(f'Invalid random color style: {name}')
    return name


def clean_style_name(name: str | AllColorStyles.Literals) -> str:
    if name.endswith(PYGMENTS_SUFFIX):
        return name[:-len(PYGMENTS_SUFFIX)]  # Remove suffix for Pygments compatibility
    elif name.startswith(ANSI_PREFIX):
        return name.replace('-', '_')  # Convert dashes to underscores for Rich compatibility
    return name


def install_base16_theme(theme_key: str) -> None:
    if theme_key not in pygments.styles.STYLES:
        base16_style_cls_name = _create_base_16_class_name_from_theme_key(theme_key)

        # Hack to register the new style class with Pygments, as it doesn't provide a public API
        # for this other than manually configuring a package entry point
        # (see: https://github.com/pygments/pygments/issues/1096)

        pygments.styles.STYLES[base16_style_cls_name] = (
            'omnipy.data._display.styles.dynamic_styles',
            theme_key,
            (),
        )
        pygments.styles._STYLE_NAME_TO_MODULE_MAP[theme_key] = (
            'omnipy.data._display.styles.dynamic_styles',
            base16_style_cls_name,
        )
