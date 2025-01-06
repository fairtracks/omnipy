from enum import Enum
import os
from types import ModuleType

import omnipy
from omnipy.util._pydantic import lenient_isinstance, lenient_issubclass

from . import (BackoffStrategy,
               ConfigOutputStorageProtocolOptions,
               ConfigPersistOutputsOptions,
               ConfigRestoreOutputsOptions,
               EngineChoice,
               OutputStorageProtocolOptions,
               PersistOutputsOptions,
               RestoreOutputsOptions,
               RunState)

# TODO: Finish implementation of dynamic __all__ generation. Possibly useful together with Poe the
#       Poet (https://poethepoet.natn.io/poetry_plugin.html) for generating a fixed __all__ list as
#       part of the build process. The goal for this functionality is to follow DRY principles and
#       make sure new datasets, models, and jobs are exported. It is important to also allow export
#       under development, either through running `poetry build` or through a
#       `if not typing.TYPE_CHECKING` block or similar solution to allow dynamic __all__ generation
#       for development (with omnipy imported through `pip install -e {PATH_TO_OMNIPY}`). The exact
#       implementation is not yet decided, but the goal is to make the code the single source of
#       truth for the exported elements of omnipy.

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
__all__: list[str] = []

_all_element_names: set[str] = set()

_exclude_modules: set[str] = {
    '_dynamic_all',
    'components._frozen',  # Recursive frozen models crashes mypy v1.10 + wait for pydantic support
    'components._fairtracks',
}
_exclude_attrs: set[str] = {
    'JobMixin',
    'JobTemplateMixin',
    'ListOfNestedStrModel',
    'SplitItemsToSubitemsModel',
    'JoinSubitemsToItemsModel',
    'QueryParamsJoinerModel',
    'QueryParamsSplitterModel',
}

_all_modules: dict[str, ModuleType] = {}

if not __all__:
    from .compute._job import JobTemplateMixin
    from .compute.flow import (DagFlow,
                               DagFlowTemplate,
                               FuncFlow,
                               FuncFlowTemplate,
                               LinearFlow,
                               LinearFlowTemplate)
    from .compute.task import Task, TaskTemplate
    from .data.dataset import Dataset, MultiModelDataset
    from .data.model import Model
    from .data.param import (bind_adjust_dataset_func,
                             bind_adjust_model_func,
                             params_dataclass,
                             ParamsBase)
    from .hub.runtime import runtime
    from .util.contexts import print_exception
    from .util.helpers import recursive_module_import_new

    __all__ = [
        'DagFlow',
        'DagFlowTemplate',
        'FuncFlow',
        'FuncFlowTemplate',
        'LinearFlow',
        'LinearFlowTemplate',
        'Task',
        'TaskTemplate',
        'Dataset',
        'MultiModelDataset',
        'Model',
        'bind_adjust_model_func',
        'bind_adjust_dataset_func',
        'params_dataclass',
        'ParamsBase',
        'runtime',
        'print_exception',
        'RestoreOutputsOptions',
        'ConfigRestoreOutputsOptions',
        'PersistOutputsOptions',
        'BackoffStrategy',
        'OutputStorageProtocolOptions',
        'ConfigPersistOutputsOptions',
        'ConfigOutputStorageProtocolOptions',
        'RunState',
        'EngineChoice',
    ]
    _all_element_names = set(__all__)

    _omnipy_all = set(omnipy.__all__)

    recursive_module_import_new([ROOT_DIR], _all_modules, _exclude_modules)

    for module_name, module in _all_modules.items():
        for attr in dir(module):
            if not attr.startswith('_') and attr not in _all_element_names:
                val = getattr(module, attr)
                if attr in _exclude_attrs or not val.__class__.__module__.startswith('omnipy'):
                    continue

                if lenient_issubclass(val, Model) \
                        or lenient_issubclass(val, Dataset) \
                        or lenient_isinstance(val, JobTemplateMixin) \
                        or lenient_issubclass(val, Enum):
                    print(f'Adding {attr}')
                    _all_element_names.add(attr)
                    globals()[attr] = val
                    __all__.append(attr)

    print(f'Missing elements in omnipy.__init__(): {_all_element_names - _omnipy_all}')
    print(f'Missing elements in hardcoded __all__ in _dynamic_all(): '
          f'{_omnipy_all - _all_element_names}')

    del JobTemplateMixin
