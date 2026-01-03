from typing import Literal, TYPE_CHECKING

# These constants should be overridden through mypy and pyright configs,
# respectively. In this way, they can be used in type checking
# conditional blocks to customize typing behavior for each type checker.
#
# For mypy (in pyproject.toml):
#   [tool.mypy]
#   always_true = TYPE_CHECKER_IS_MYPY
#
# For pyright (in pyproject.toml):
#   [tool.pyright]
#   defineConstant = { TYPE_CHECKER = 'pyright'}
#
#  Use the TYPE_CHECKER constant to reveal which type checker is being
#  used, e.g.:
#
#  ```python
#  from omnipy.shared.typing import TYPE_CHECKER, TYPE_CHECKING
#
#  if TYPE_CHECKING:
#      if TYPE_CHECKER == 'mypy':
#          # mypy-specific typing code
#      elif TYPE_CHECKER == 'pyright':
#          # pyright-specific typing code
#      else:  # 'unknown'
#          # DO NOT normally include typing code in case of 'unknown'
#      # INSTEAD, generic typing code for all type checkers goes outside
#      # the TYPE_CHECKER conditional block
#  ```
#
#  If no config constants are set for either type checker, TYPE_CHECKER
#  will be set to 'unknown'.

TYPE_CHECKER_IS_MYPY = False
# No type to allow mypy to override the value through config

if not TYPE_CHECKER_IS_MYPY:
    # mypy behavior:
    #   mypy sets the _TYPE_CHECKER type according to the FIRST
    #   definition it encounters (here, given that TYPE_CHECKER_IS_MYPY
    #   is not set to True in the mypy config)
    _TYPE_CHECKER: Literal['unknown'] = 'unknown'  # pyright: ignore

if TYPE_CHECKER_IS_MYPY:
    _TYPE_CHECKER: Literal['mypy'] = 'mypy'  # type: ignore[no-redef]
else:
    # pyright behavior:
    #   in contrast to mypy, pyright sets the _TYPE_CHECKER type
    #   according to the LAST possible definition
    _TYPE_CHECKER: Literal['unknown'] = 'unknown'  # type: ignore[no-redef]

TYPE_CHECKER = _TYPE_CHECKER
# No type to allow pyright to override the value through config

if TYPE_CHECKER == 'unknown':
    # TYPE_CHECKER is not set in the pyright config. Set the type of
    # TYPE_CHECKER to allow pyright to correctly infer types in this
    # case.
    TYPE_CHECKER: Literal['mypy', 'pyright', 'unknown']  # type: ignore[no-redef]

# We do not want to export TYPE_CHECKER_IS_MYPY
del TYPE_CHECKER_IS_MYPY

# Exports
TYPE_CHECKER
TYPE_CHECKING
