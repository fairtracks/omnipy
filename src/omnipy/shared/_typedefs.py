"""Private shared type variables used across Omnipy protocol definitions."""

from typing import TypeVar

_JobT = TypeVar('_JobT', covariant=True)
_JobTemplateT = TypeVar('_JobTemplateT', covariant=True)
