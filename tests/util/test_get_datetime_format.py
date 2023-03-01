import os

import pytest

from omnipy.util.helpers import get_datetime_format


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Not trivial to test default locale and a test is probably not needed. The current
test assumes the default locale is "en_US.UTF-8", but that is probably an incorrect
assumption.
""")
def test_default():
    assert get_datetime_format() == '%a %b %e %X %Y'


def test_different_locale():
    # TDDD: Add new platforms as needed
    assert get_datetime_format(('de_DE', 'UTF-8')) in (
        '%a %e %b %X %Y',  # MacOS
        '%a %d %b %Y %T %Z',  # Ubuntu
    )
