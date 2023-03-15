from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeAlias, TypeVar, Union

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = Union[str, Tuple[Optional[str], Optional[str]]]
JobBaseT = TypeVar('JobBaseT', bound='JobBase', covariant=True)
JobT = TypeVar('JobT', bound='JobMixin', covariant=True)
JobTemplateT = TypeVar('JobTemplateT', bound='JobTemplateMixin', covariant=True)
FuncJobTemplateT = TypeVar('FuncJobTemplateT', bound='FuncJobTemplate', covariant=True)
TaskTemplatesFlowTemplateT = TypeVar(
    'TaskTemplatesFlowTemplateT', bound='TaskTemplatesFlowTemplate', covariant=True)
FlowT = TypeVar('FlowT', bound='Flow', covariant=True)
FlowBaseT = TypeVar('FlowBaseT', bound='FlowBase', covariant=True)
FlowTemplateT = TypeVar('FlowTemplateT', bound='FlowTemplate', covariant=True)
