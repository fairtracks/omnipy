from datetime import date, datetime
from typing import Union

import omnipy.util._pydantic as pyd

# TODO: Remove date/datetime validator with pydantic v2, `model_dump(mode='json')` should fix it
#       (see https://github.com/pydantic/pydantic/issues/1409#issuecomment-1423995424).


def date_to_iso_format(data: Union[datetime, date, pyd.constr(max_length=0)]):
    if isinstance(data, date) or isinstance(data, datetime):
        return data.isoformat()
    return data
