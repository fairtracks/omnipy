"""Shared fixtures for data display panel tests."""

import pytest_cases as pc


@pc.fixture
def common_content() -> str:
    """Provide common content."""
    return ("[MyClass({'abc': [123, 234]}),\n"
            " MyClass({'def': [345, 456]})]")


@pc.fixture
def common_text_content() -> str:
    """Provide common text content."""
    return ("[MyClass({'abc': [123, 234]}),\n"
            " MyClass({'def': [345, 456]})]")
