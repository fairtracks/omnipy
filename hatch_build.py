"""Hatch metadata hook setting the package readme from `README.md` with absolute image URLs.

`README.md` links its images relative to the repository root, which GitHub resolves against the
revision being viewed. PyPI shows the readme from the package metadata and needs absolute URLs
that keep showing the images of the released version, so the links are rewritten when the package
is built: to the raw GitHub URLs of the release tag, or of the commit for a build without one.
"""

from pathlib import Path
import re
import subprocess

from hatchling.metadata.plugin.interface import MetadataHookInterface

REPO_RAW_URL = 'https://raw.githubusercontent.com/fairtracks/omnipy/{ref}/'
RELEASE_TAG_PATTERN = 'omnipy_v*'
RELEASE_VERSION_RE = re.compile(r'^\d+\.\d+\.\d+((a|b|rc)\d+)?(\.post\d+)?$')
REPO_LINK_RE = re.compile(r'\]\((docs/[^)\s]+)\)')


class ReadmeMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = 'custom'

    def update(self, metadata: dict) -> None:
        root = Path(self.root)
        readme = (root / 'README.md').read_text(encoding='utf-8')
        base_url = REPO_RAW_URL.format(ref=_git_ref(root))
        readme = REPO_LINK_RE.sub(lambda match: f']({base_url}{match.group(1)})', readme)
        metadata['readme'] = {'content-type': 'text/markdown', 'text': readme}


def _git_ref(root: Path) -> str:
    """The release tag of the checkout, else its commit, else the version of the sdist."""

    def git(*args: str) -> str | None:
        try:
            return subprocess.run(
                ['git', *args], cwd=root, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    release_tag = git('describe', '--tags', '--exact-match', '--match', RELEASE_TAG_PATTERN)
    if release_tag:
        return release_tag

    commit = git('rev-parse', 'HEAD')
    if commit:
        return commit

    # Building a wheel from an sdist: no git checkout, but the version is in PKG-INFO
    pkg_info = root / 'PKG-INFO'
    if pkg_info.exists():
        for line in pkg_info.read_text(encoding='utf-8').splitlines():
            if line.startswith('Version: '):
                version = line.removeprefix('Version: ').strip()
                if RELEASE_VERSION_RE.match(version):
                    return f'omnipy_v{version}'
                break

    return 'main'
