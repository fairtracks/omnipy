import asyncio
from functools import cache

import aiohttp
from inflection import dasherize, underscore
import pygments.style
import pygments.styles
from ruamel.yaml import YAML

from omnipy.data._display.styles.helpers import Base16Theme, get_styles_from_base16_colors

_BASE16_DOWNLOAD_URL = ('https://raw.githubusercontent.com/tinted-theming/'
                        'schemes/refs/heads/spec-0.11/base16/')
_STYLE_CLS_NAME_BASE16_PREFIX = 'TintedBase16'
_STYLE_CLS_NAME_SUFFIX = 'Style'
_THEME_KEY_BASE16_PREFIX = 'tb16-'


class TintedBase16Style(pygments.style.Style):
    name: str
    author: str
    variant: str


async def _get_response(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise IOError(f'Failed to fetch "{url}", returned: {resp.status}')
            return await resp.text()


async def fetch_base16_theme(theme_url: str) -> Base16Theme:
    base16_theme_yaml = await _get_response(theme_url)

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


def _create_base_16_class_name_from_theme_key(base16_theme_name: str):
    assert base16_theme_name.startswith(_THEME_KEY_BASE16_PREFIX)
    base16_theme_name_stripped = base16_theme_name[len(_THEME_KEY_BASE16_PREFIX):]

    class_name = (f'{_STYLE_CLS_NAME_BASE16_PREFIX}'
                  f"{_capitalize_words(underscore(base16_theme_name_stripped)).replace(' ', '')}"
                  f'{_STYLE_CLS_NAME_SUFFIX}')

    return class_name


def _capitalize_words(text: str) -> str:
    return ' '.join(word.capitalize() for word in text.split())


@cache
def __getattr__(attr: str) -> type[pygments.style.Style]:
    try:
        if attr.startswith(_STYLE_CLS_NAME_BASE16_PREFIX) and attr.endswith(_STYLE_CLS_NAME_SUFFIX):
            stripped_name = attr[len(_STYLE_CLS_NAME_BASE16_PREFIX):-len(_STYLE_CLS_NAME_SUFFIX)]

            core_name = dasherize(underscore(stripped_name))
            filename = core_name + '.yaml'
            theme_key = _THEME_KEY_BASE16_PREFIX + core_name

            base16_url = f'{_BASE16_DOWNLOAD_URL}/{filename}'
            loop = asyncio.get_event_loop()
            base16_theme = loop.run_until_complete(fetch_base16_theme(base16_url))

            return create_dynamic_base16_style_class(theme_key, base16_theme)

    except (IOError, ValueError) as e:
        raise AttributeError(f'Failed to fetch base16 theme: {e}') from e

    raise AttributeError(f"Module '{__name__}' has no attribute '{attr}'")


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
