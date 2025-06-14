import asyncio
from contextlib import contextmanager
import random
from textwrap import dedent
from typing import Annotated, Any, AsyncGenerator, Awaitable, Callable, Iterator

from aiohttp import web
import pygments.style
import pygments.styles
import pygments.token
import pytest
import pytest_cases as pc

from omnipy.data._display.config import AllColorStyles
from omnipy.data._display.styles.dynamic_styles import (create_dynamic_base16_style_class,
                                                        fetch_base16_theme,
                                                        install_base16_theme,
                                                        TintedBase16Style)
from omnipy.data._display.styles.helpers import Base16Colors, Base16Theme
from omnipy.util.contexts import hold_and_reset_prev_attrib_value

from ....helpers.functions import get_pip_installed_packages

# mypy: disable-error-code="attr-defined"
# pyright: reportAttributeAccessIssue=none


@pc.fixture
def example_base16_theme_yaml() -> str:
    return dedent("""
        system: "base16"
        name: "Example 1"
        author: "John Doe"
        variant: "light"
        palette:
            base00: "#ffffff" #  ----
            base01: "#dddddd" #  ---
            base02: "#bbbbbb" #  --
            base03: "#999999" #  -
            base04: "#666666" #  +
            base05: "#444444" #  ++
            base06: "#222222" #  +++
            base07: "#000000" #  ++++
            base08: "#ff0000" #	red
            base09: "#ffaf00" #	orange
            base0A: "#ffff00" #	yellow
            base0B: "#00ff00" #	green
            base0C: "#00ffff" #	aqua
            base0D: "#0000ff" #	blue
            base0E: "#8700af" #	purple
            base0F: "#875f00" #	brown
        """)


@pc.fixture
def example_base2_theme_yaml() -> str:
    return dedent("""
        system: "base2"
        name: "Example Base2"
        author: "John Doe"
        variant: "light"
        palette:
            base00: "ffffff"
            base01: "000000"
        """)


@pc.fixture
def example_base16_theme() -> Base16Theme:
    return Base16Theme(
        name='Example 1',
        author='John Doe',
        variant='light',
        palette=Base16Colors(
            base00='#ffffff',
            base01='#dddddd',
            base02='#bbbbbb',
            base03='#999999',
            base04='#666666',
            base05='#444444',
            base06='#222222',
            base07='#000000',
            base08='#ff0000',
            base09='#ffaf00',
            base0A='#ffff00',
            base0B='#00ff00',
            base0C='#00ffff',
            base0D='#0000ff',
            base0E='#8700af',
            base0F='#875f00',
        ),
    )


async def _get_endpoint_url(
    aiohttp_server,
    endpoint_path: str,
    example_theme_yaml: str,
) -> str:
    async def _my_endpoint(request: web.Request) -> web.Response:
        return web.Response(text=example_theme_yaml)

    def _create_app() -> web.Application:
        app = web.Application()
        app.router.add_route('GET', endpoint_path, _my_endpoint)
        return app

    server = await aiohttp_server(_create_app())
    return str(server.make_url(endpoint_path))


@pc.fixture(scope='function')
async def my_base16_endpoint_url(
    aiohttp_server,
    example_base16_theme_yaml: Annotated[str, pytest.fixture],
) -> AsyncGenerator[str, None]:
    yield await _get_endpoint_url(aiohttp_server, '/example-1.yaml', example_base16_theme_yaml)


@pc.fixture(scope='function')
async def my_base2_endpoint_url(
    aiohttp_server,
    example_base2_theme_yaml: Annotated[str, pytest.fixture],
) -> AsyncGenerator[str, None]:
    yield await _get_endpoint_url(aiohttp_server, '/example-2.yaml', example_base2_theme_yaml)


@pc.fixture(scope='function')
def run_sync_func() -> Callable[[Callable[..., Any]], Awaitable[Any]]:
    """
    Fixture to run blocking synchronous functions in an async context.
    """
    async def _run_sync_func(func: Callable[..., Any]) -> Any:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, func)

    return _run_sync_func


async def test_fetch_base16_theme(
    my_base16_endpoint_url: Annotated[str, pytest.fixture],
    example_base16_theme: Annotated[Base16Theme, pytest.fixture],
    run_sync_func: Annotated[Callable[[Callable[..., Any]], Awaitable[Any]], pytest.fixture],
) -> None:
    def _test_fetch_base16_theme():
        base16_theme_output = fetch_base16_theme(my_base16_endpoint_url)
        assert base16_theme_output == example_base16_theme

    run_sync_func(_test_fetch_base16_theme)


async def test_fail_incorrect_system_fetch_base2_theme(
    my_base2_endpoint_url: Annotated[str, pytest.fixture],
    run_sync_func: Annotated[Callable[[Callable[..., Any]], Awaitable[Any]], pytest.fixture],
) -> None:
    def _test_fail_incorrect_system_fetch_base2_theme():
        with pytest.raises(ValueError):
            fetch_base16_theme(my_base2_endpoint_url)

    run_sync_func(_test_fail_incorrect_system_fetch_base2_theme)


def _assert_example_base16_style(TintedBase16Example_1Style: type[pygments.style.Style],
                                 example_theme: Base16Theme):
    assert issubclass(TintedBase16Example_1Style, pygments.style.Style)
    assert issubclass(TintedBase16Example_1Style, TintedBase16Style)
    assert TintedBase16Example_1Style.__name__ == 'TintedBase16Example_1Style'
    assert TintedBase16Example_1Style.name == example_theme.name
    assert TintedBase16Example_1Style.author == example_theme.author
    assert TintedBase16Example_1Style.variant == example_theme.variant
    assert TintedBase16Example_1Style.background_color == example_theme.palette.base00
    assert TintedBase16Example_1Style.highlight_color == example_theme.palette.base02
    assert TintedBase16Example_1Style.styles[pygments.token.Text] == example_theme.palette.base05


def test_create_dynamic_style_class(example_base16_theme: Annotated[Base16Theme, pytest.fixture]):
    TintedBase16Example_1Style = create_dynamic_base16_style_class(
        'tb16-example-1',
        example_base16_theme,
    )
    _assert_example_base16_style(TintedBase16Example_1Style, example_base16_theme)


def test_fail_create_dynamic_style_class_incorrect_theme_suffix(
        example_base16_theme: Annotated[Base16Theme, pytest.fixture]) -> None:
    with pytest.raises(AssertionError):
        create_dynamic_base16_style_class('my-example-1', example_base16_theme)


@contextmanager
def _setup_base16_download_url(my_base16_endpoint_url: str) -> Iterator[None]:
    import omnipy.data._display.styles.dynamic_styles
    domain_url = '/'.join(my_base16_endpoint_url.split('/')[:-1])
    with hold_and_reset_prev_attrib_value(
            omnipy.data._display.styles.dynamic_styles,
            '_BASE16_DOWNLOAD_URL',
    ):
        omnipy.data._display.styles.dynamic_styles._BASE16_DOWNLOAD_URL = domain_url
        yield


async def test_auto_create_dynamic_style_class_at_import(
    example_base16_theme: Annotated[Base16Theme, pytest.fixture],
    my_base16_endpoint_url: Annotated[str, pytest.fixture],
    run_sync_func: Annotated[Callable[[Callable[..., Any]], Awaitable[Any]], pytest.fixture],
):
    def _test_auto_create_dynamic_style_class_at_import():
        with _setup_base16_download_url(my_base16_endpoint_url):
            from omnipy.data._display.styles.dynamic_styles import TintedBase16Example_1Style
            style_cls = TintedBase16Example_1Style
            _assert_example_base16_style(style_cls, example_base16_theme)

    await run_sync_func(_test_auto_create_dynamic_style_class_at_import)


async def test_install_base16_theme(
    example_base16_theme: Annotated[Base16Theme, pytest.fixture],
    my_base16_endpoint_url: Annotated[str, pytest.fixture],
    run_sync_func: Annotated[Callable[[Callable[..., Any]], Awaitable[Any]], pytest.fixture],
):
    def _test_install_base16_theme():
        with _setup_base16_download_url(my_base16_endpoint_url):
            install_base16_theme('tb16-example-1')
            _assert_example_base16_style(
                pygments.styles.get_style_by_name('tb16-example-1'),
                example_base16_theme,
            )

    await run_sync_func(_test_install_base16_theme)


async def test_fail_install_base16_theme_incorrect_theme_suffix(
    example_base16_theme: Annotated[Base16Theme, pytest.fixture],
    my_base16_endpoint_url: Annotated[str, pytest.fixture],
    run_sync_func: Annotated[Callable[[Callable[..., Any]], Awaitable[Any]], pytest.fixture],
):
    def _test_fail_install_base16_theme_incorrect_theme_suffix():
        with pytest.raises(AssertionError):
            with _setup_base16_download_url(my_base16_endpoint_url):
                install_base16_theme('my-example-1')

    await run_sync_func(_test_fail_install_base16_theme_incorrect_theme_suffix)


async def test_fail_import_missing(
    example_base16_theme: Annotated[Base16Theme, pytest.fixture],
    my_base16_endpoint_url: Annotated[str, pytest.fixture],
    run_sync_func: Annotated[Callable[[Callable[..., Any]], Awaitable[Any]], pytest.fixture],
):
    def _test_fail_import_missing():
        with _setup_base16_download_url(my_base16_endpoint_url):
            with pytest.raises(ImportError):
                from omnipy.data._display.styles.dynamic_styles import \
                    TintedBase16MissingStyle  # noqa

            with pytest.raises(ImportError):
                from omnipy.data._display.styles.dynamic_styles import something_else  # noqa

    await run_sync_func(_test_fail_import_missing)


def test_omnipy_style_import() -> None:
    # To make sure the tests only run when the omnipy package is installed, which is required for
    # the styles to be registered with the pygments package. This is needed as the tests might be
    # run in a development environment where the omnipy package is not installed.

    if 'omnipy' in get_pip_installed_packages():

        IGNORE_PREFIXES = ['tb16-', 'ansi_']

        installed_styles = [
            style for style in AllColorStyles.values()
            if not any(style.startswith(prefix) for prefix in IGNORE_PREFIXES)
        ]
        for style in installed_styles:
            pygments.styles.get_style_by_name(style)


def test_dynamic_style_import() -> None:
    installable_styles = [style for style in AllColorStyles.values() if style.startswith('tb16-')]

    for style in random.sample(installable_styles, 3):
        print(f'Installing style: {style}...')
        install_base16_theme(style)

        pygments.styles.get_style_by_name(style)
