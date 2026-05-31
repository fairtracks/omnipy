# flake8: noqa
"""Re-export placeholder objects used for fluent callable expressions.

This module centralizes Omnipy's imports from the third-party ``placeholder``
package so internal code can consistently import ``F``, ``m``, and ``x`` from a
single location. These objects are primarily used to build concise functional and
method-call placeholder expressions.
"""

#: Generic placeholder object exported as ``x`` for concise expression building.
#: Method-call placeholder exported from the ``placeholder`` package.
#: Functional placeholder exported from the ``placeholder`` package.
from placeholder import _ as x
from placeholder import F, m
