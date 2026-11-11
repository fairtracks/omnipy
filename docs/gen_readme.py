"""Generate the root `README.md` and `docs/images/readme/*.svg` from `docs/readme.md`.

`docs/readme.md` is written for MkDocs with markdown-exec: its examples run when the documentation
is built, and the displays are HTML. GitHub and PyPI show a README as it is, so this script runs
the same examples and writes a static Markdown file, with the displays as SVG images and the code
listings as plain code blocks.

Run from the repository root, after editing `docs/readme.md`:

    uv run python docs/gen_readme.py
"""

from collections.abc import Iterator
import contextlib
import io
from pathlib import Path
import re
import sys
from typing import NamedTuple

import rich.console

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'docs' / 'readme.md'
TARGET = ROOT / 'README.md'
IMAGE_DIR = ROOT / 'docs' / 'images' / 'readme'
INCLUDES_DIR = ROOT / 'docs' / '_includes'
DOCS_SITE_URL = 'https://omnipy.readthedocs.io/en/latest/'

HIDE_MARKER = '# markdown-exec: hide'
PROMPTS = ('>>> ', '... ')
# Rich exports SVGs for a 20px font; the readme shows them at 15px
SVG_SCALE = 0.75

FENCE_RE = re.compile(r'^```(\w*)\s*(.*)$')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
INCLUDE_RE = re.compile(r'^--8<-- "([^"]+)"$')
DOCS_CALL_RE = re.compile(r'^print\((?P<obj>.+?)\._docs\((?P<args>.*)\)\)$', re.S)
ADMONITION_RE = re.compile(r'^!!! \w+ "(?P<title>[^"]+)"\n\n    ```\n(?P<body>.*?)    ```', re.S)
MD_LINK_RE = re.compile(r'\]\(([\w./-]+\.md)\)')
IMAGE_LINK_RE = re.compile(r'\]\(images/')
VIEWBOX_RE = re.compile(r'viewBox="[\d. ]+"')
MATRIX_OFFSET_RE = re.compile(r'<g transform="translate\(([\d.]+), ([\d.]+)\)"')
BACKGROUND_SIZE_RE = re.compile(r'<rect x="0" y="0" width="([\d.]+)" height="([\d.]+)"')

GENERATED_NOTE = (
    '<!-- Generated from docs/readme.md by docs/gen_readme.py. Edit the source and regenerate. -->'
)
GETTING_STARTED_NOTE = (
    'The examples below run when the documentation is built, and their output is shown here as '
    'images. The [documentation site](https://omnipy.readthedocs.io/) shows the same page with '
    'live output, and is the place to copy from.'
)


class Fence(NamedTuple):
    lang: str
    attrs: dict[str, str]
    lines: list[str]


def _iter_blocks(lines: list[str]) -> Iterator[str | Fence]:
    """Yield text lines and fenced code blocks of a Markdown file."""
    i = 0
    while i < len(lines):
        match = FENCE_RE.match(lines[i])
        if match and not lines[i].startswith('````'):
            lang, attr_str = match.groups()
            attrs = dict(ATTR_RE.findall(attr_str))
            body = []
            i += 1
            while i < len(lines) and lines[i] != '```':
                body.append(lines[i])
                i += 1
            yield Fence(lang, attrs, body)
        else:
            yield lines[i]
        i += 1


def _expand_includes(lines: list[str]) -> list[str]:
    expanded = []
    for line in lines:
        match = INCLUDE_RE.match(line)
        if match:
            expanded.extend((ROOT / 'docs' / match.group(1)).read_text().splitlines())
        else:
            expanded.append(line)
    return expanded


def _pycon_code(lines: list[str]) -> str:
    return '\n'.join(line[4:] for line in lines if line.startswith(PROMPTS))


def _visible_lines(lines: list[str]) -> list[str]:
    visible = [line for line in lines if HIDE_MARKER not in line and not INCLUDE_RE.match(line)]
    while visible and not visible[0].strip():
        visible.pop(0)
    while visible and not visible[-1].strip():
        visible.pop()
    return visible


def _run(code: str, namespace: dict) -> str:
    with contextlib.redirect_stdout(io.StringIO()) as output:
        exec(compile(code, '<readme>', 'exec'), namespace)
    return output.getvalue().rstrip()


def _render_svg(obj_expr: str, args: str, namespace: dict, path: Path) -> None:
    """Render the display `obj_expr._docs(args)` to an SVG file with the colours of the docs."""
    from omnipy.data._display.panel.helpers import ForceAutodetect

    separator = ', ' if args.strip() else ''
    panel = eval(f'({obj_expr})._docs({args}{separator}return_draft_panel=True)', namespace)
    while True:
        try:
            panel = panel.render_next_stage()
        except NotImplementedError:
            break

    variant = panel.colorized
    console = variant._prepare_html_console_according_to_output_mode()
    theme = variant._prepare_color_theme_for_html(
        force_autodetect=ForceAutodetect.IF_NO_BG_COLOR_IN_STYLE
    )
    svg = console.export_svg(
        title='',
        clear=False,
        theme=theme,
        code_format=rich.console.CONSOLE_SVG_FORMAT.replace('{chrome}', ''),
    )

    # The embedded web font is blocked by GitHub and PyPI; the fallback is a monospace font
    svg = re.sub(r'@font-face\s*\{[^}]*\}', '', svg)

    # Crop to the terminal background, leaving out the space reserved for the chrome
    offset_x, offset_y = MATRIX_OFFSET_RE.search(svg).groups()
    width, height = BACKGROUND_SIZE_RE.search(svg).groups()
    svg = VIEWBOX_RE.sub(f'viewBox="{offset_x} {offset_y} {width} {height}"', svg, count=1)
    svg = svg.replace(
        '<svg ',
        f'<svg width="{float(width) * SVG_SCALE:.0f}" height="{float(height) * SVG_SCALE:.0f}" ',
        1,
    )
    path.write_text('\n'.join(line.rstrip() for line in svg.splitlines()) + '\n')


def _slug(text: str) -> str:
    return re.sub(r'\W+', '-', text).strip('-')[:40] or 'display'


def _convert_text_line(line: str) -> str:
    line = MD_LINK_RE.sub(lambda m: f']({DOCS_SITE_URL}{m.group(1)[:-3]}/)', line)
    return IMAGE_LINK_RE.sub('](docs/images/', line)


class ReadmeGenerator:
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}
        self._output: list[str] = []
        # A non-executed console block waits for the output of the executed block following it
        self._pending_fence: list[str] | None = None
        self._pending_fence_has_output = False
        self._image_count = 0

    def generate(self) -> None:
        import omnipy as om

        # Images need a background of their own, as the page behind them may be dark or light
        om.runtime.config.data.ui.browser.color.solid_background = True

        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        for old_image in IMAGE_DIR.glob('*.svg'):
            old_image.unlink()

        self._output.append(GENERATED_NOTE)
        for block in _iter_blocks(SOURCE.read_text().splitlines()):
            if isinstance(block, Fence):
                self._handle_fence(block)
            else:
                self._handle_text(block)
        self._close_pending_fence()

        text = re.sub(r'\n{3,}', '\n\n', '\n'.join(self._output)).rstrip() + '\n'
        TARGET.write_text(text)

    # Text

    def _handle_text(self, line: str) -> None:
        if self._pending_fence is not None and (line.strip() or self._pending_fence_has_output):
            self._close_pending_fence()
        self._output.append(_convert_text_line(line))
        if line == '## Getting started':
            self._output.extend(['', GETTING_STARTED_NOTE])

    # Fences

    def _handle_fence(self, fence: Fence) -> None:
        if fence.attrs.get('exec') != '1':
            if fence.lang == 'pycon':
                self._open_pending_fence(fence.lines)
            else:
                self._emit_fence(fence.lang, fence.lines)
            return

        namespace = self._sessions.setdefault(
            fence.attrs.get('session', ''), {'__name__': '__main__'}
        )
        if fence.lang == 'python':
            self._handle_python_listing(fence, namespace)
        elif fence.lang == 'pycon':
            self._handle_pycon(fence, namespace)
        else:
            raise ValueError(f'Unsupported executable fence: {fence.lang} {fence.attrs}')

    def _handle_python_listing(self, fence: Fence, namespace: dict) -> None:
        # The block defines `code`, executes it and displays it. The code is shown as is.
        _run('\n'.join(fence.lines), namespace)
        self._emit_fence('python', str(namespace['code']).rstrip().splitlines())

    def _handle_pycon(self, fence: Fence, namespace: dict) -> None:
        lines = _expand_includes(fence.lines)
        code = _pycon_code(lines)

        if fence.attrs.get('html') == 'true':
            match = DOCS_CALL_RE.match(code.strip())
            if match is None:
                raise ValueError(f'Expected a single print(x._docs(...)) call, got:\n{code}')
            self._emit_image(match['obj'], match['args'], namespace)
            return

        output = _run(code, namespace)
        if 'source' in fence.attrs:
            self._close_pending_fence()
            self._emit_fence('pycon', _visible_lines(lines) + output.splitlines())
        elif output:
            self._append_output(_convert_admonition(output).splitlines())

    # Output

    def _emit_image(self, obj_expr: str, args: str, namespace: dict) -> None:
        self._close_pending_fence()
        self._image_count += 1
        name = f'{self._image_count:02d}-{_slug(obj_expr)}.svg'
        _render_svg(obj_expr, args, namespace, IMAGE_DIR / name)
        self._output.extend(['', f'![Display of {obj_expr}](docs/images/readme/{name})', ''])

    def _emit_fence(self, lang: str, lines: list[str]) -> None:
        self._close_pending_fence()
        self._output.extend([f'```{lang}', *lines, '```'])

    def _open_pending_fence(self, lines: list[str]) -> None:
        self._close_pending_fence()
        self._pending_fence = list(lines)

    def _append_output(self, lines: list[str]) -> None:
        if self._pending_fence is None:
            self._pending_fence = []
        self._pending_fence.extend(lines)
        self._pending_fence_has_output = True

    def _close_pending_fence(self) -> None:
        if self._pending_fence is not None:
            self._output.extend(['```pycon', *self._pending_fence, '```', ''])
            self._pending_fence = None
            self._pending_fence_has_output = False


def _convert_admonition(output: str) -> str:
    """Turn the docs' failure admonition into the last lines of a console traceback."""
    match = ADMONITION_RE.match(output)
    if match is None:
        return output
    body = [line[4:] if line.startswith('    ') else line for line in match['body'].splitlines()]
    return '\n'.join([f'{match["title"]}: {body[0]}', *body[1:]])


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    ReadmeGenerator().generate()
    print(f'Wrote {TARGET.relative_to(ROOT)} and {len(list(IMAGE_DIR.glob("*.svg")))} images')
