from typing import TypeVar

_JobT = TypeVar('_JobT', covariant=True)
_JobTemplateT = TypeVar('_JobTemplateT', covariant=True)
_TaskTemplateT = TypeVar('_TaskTemplateT')
_TaskTemplateContraT = TypeVar('_TaskTemplateContraT', contravariant=True)
_TaskTemplateCovT = TypeVar('_TaskTemplateCovT', covariant=True)
