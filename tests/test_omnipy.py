"""Tests for omnipy."""

from importlib.metadata import version

from omnipy import __version__


def test_version():
    assert __version__ == version('omnipy')
