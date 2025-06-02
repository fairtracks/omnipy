import pytest_cases as pc


@pc.fixture
def common_content() -> str:
    return ("[MyClass({'abc': [123, 234]}),\n"
            " MyClass({'def': [345, 456]})]")


@pc.fixture
def common_text_content() -> str:
    return ("[MyClass({'abc': [123, 234]}),\n"
            " MyClass({'def': [345, 456]})]")
