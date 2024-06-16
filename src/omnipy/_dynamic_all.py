import os
from types import ModuleType

from pydantic.utils import lenient_isinstance, lenient_issubclass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
__all__: list[str] = []

_all_element_names: set[str] = set()

_exclude_modules: set[str] = {
    '_dynamic_all', 'modules.frozen', 'modules.fairtracks', 'util.tabulate'
}
_exclude_attrs: set[str] = {'JobMixin', 'JobTemplateMixin'}

_all_modules: dict[str, ModuleType] = {}

if not __all__:
    from .compute.flow import (DagFlow,
                               DagFlowTemplate,
                               FuncFlow,
                               FuncFlowTemplate,
                               LinearFlow,
                               LinearFlowTemplate)
    from .compute.job import JobTemplateMixin
    from .compute.task import Task, TaskTemplate
    from .data.dataset import Dataset, ListOfParamModelDataset, MultiModelDataset, ParamDataset
    from .data.helpers import Params
    from .data.model import ListOfParamModel, Model, ParamModel
    from .hub.runtime import runtime
    from .util.helpers import recursive_module_import_new

    __all__ = [
        'runtime',
        'DagFlow',
        'DagFlowTemplate',
        'FuncFlow',
        'FuncFlowTemplate',
        'LinearFlow',
        'LinearFlowTemplate',
        'Task',
        'TaskTemplate',
        'Dataset',
        'ParamDataset',
        'ListOfParamModelDataset',
        'MultiModelDataset',
        'Params',
        'Model',
        'ParamModel',
        'ListOfParamModel'
    ]
    _all_element_names = set(__all__)

    recursive_module_import_new([ROOT_DIR], _all_modules, _exclude_modules)

    for module_name, module in _all_modules.items():
        for attr in dir(module):
            if not attr.startswith('_') and not attr in _all_element_names:
                val = getattr(module, attr)
                if attr in _exclude_attrs:
                    continue

                if lenient_issubclass(val, Model) \
                        or lenient_issubclass(val, Dataset) \
                        or lenient_isinstance(val, JobTemplateMixin):
                    _all_element_names.add(attr)
                    globals()[attr] = val
                    __all__.append(attr)

    del JobTemplateMixin

# from omnipy import __all__ as prev_all
#
# prev_all_set = set(prev_all)
#
# print(f'__all__: {__all__}')
# print(
#     f'_all_element_names - prev_all: {[_ for _ in __all__ if _ in (_all_element_names - prev_all_set)]}'
# )
# print(
#     f'prev_all - _all_element_names: {[_ for _ in prev_all if _ in (prev_all_set - _all_element_names)]}'
# )
