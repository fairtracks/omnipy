"""Validation helpers shared by ISA schema models."""

from datetime import date, datetime
from typing import Union

import omnipy.util.pydantic as pyd

# TODO: Remove date/datetime validator with pydantic v2, `model_dump(mode='json')` should fix it
#       (see https://github.com/pydantic/pydantic/issues/1409#issuecomment-1423995424).


def date_to_iso_format(data: Union[datetime, date, pyd.constr(max_length=0)]):
    """Convert date-like values to their ISO-8601 string form.

    Args:
        data: Value to normalize. ``date`` and ``datetime`` instances are
            converted with ``isoformat()``, while empty-string constrained
            values are returned unchanged.

    Returns:
        ISO-8601 formatted string for date-like inputs, otherwise the original
        value.
    """

    if isinstance(data, date) or isinstance(data, datetime):
        return data.isoformat()
    return data
