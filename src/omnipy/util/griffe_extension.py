import inspect

import griffe
from griffe.agents.inspector import _convert_object_to_annotation, _convert_parameter

logger = griffe.get_logger('griffe_dyn_signature_specific_functions')


class UseDynamicSignatureForSpecificFunctions(griffe.Extension):
    def __init__(self, functions: list[str]) -> None:
        self.functions = functions

    def on_function(self, *, func: griffe.Function, **kwargs) -> None:
        if func.path not in self.functions:
            return

        try:
            runtime_func = griffe.dynamic_import(func.path)
        except ImportError as error:
            logger.warning(f'Could not import {func.path}: {error}')
            return

        # Update default values modified by decorator.
        signature = inspect.signature(runtime_func)

        parameters = griffe.Parameters(
            *[
                _convert_parameter(parameter, parent=func.parent)
                for parameter in signature.parameters.values()
            ],)
        return_annotation = signature.return_annotation
        returns = (None if return_annotation is inspect.Signature.empty else
                   _convert_object_to_annotation(return_annotation, parent=func.parent))

        func.parameters = parameters
        func.returns = returns
