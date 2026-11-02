"""Tests for omnipy."""

from importlib.metadata import version

from omnipy import __version__


def test_version():
    # Run `uv pip install -e .` to update the version in `omnipy/__init__.py`.
    assert __version__ == version('omnipy')
