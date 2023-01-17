import pytest

from omnipy.util.helpers import get_datetime_format


@pytest.mark.skip(reason="""
Not trivial to test default locale and a test is probably not needed. The current
test assumes the default locale is "en_US.UTF-8", but that is probably an incorrect
assumption.
""")
def test_default():
    assert get_datetime_format() == '%a %b %e %X %Y'


def test_different_locale():
    assert get_datetime_format(('no_NO', 'UTF-8')) == '%a %e %b %X %Y'
