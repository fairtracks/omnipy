"""Griffe extensions used when generating Omnipy API documentation.

This module customizes mkdocstrings/griffe introspection for functions whose
runtime signatures are more accurate than their statically discovered ones. The
extension re-imports selected callables and replaces the documented signature
with the runtime version so generated reference pages match actual usage.
"""

import inspect

import griffe

#: Logger used while patching selected griffe function signatures.
logger = griffe.get_logger('griffe_dyn_signature_specific_functions')


class UseDynamicSignatureForSpecificFunctions(griffe.Extension):
    """Replace griffe-discovered signatures for specific documented functions.

    Args:
        functions: Fully qualified function paths that should be re-imported and
            documented using ``inspect.signature`` at runtime.
    """
    def __init__(self, functions: list[str]) -> None:
        self.functions = functions

    def on_function_instance(self, *, func: griffe.Function, **kwargs) -> None:
        from griffe._internal.agents.inspector import (_convert_object_to_annotation,
                                                       _convert_parameter)

        if func.path not in self.functions:
            return

        try:
            runtime_func = griffe.dynamic_import(func.path)
        except ImportError as error:
            logger.warning(f'Could not import {func.path}: {error}')
            return

        signature = inspect.signature(runtime_func)

        assert func.parent is not None
        parameters = griffe.Parameters(*[
            _convert_parameter(parameter, parent=func.parent)
            for parameter in signature.parameters.values()
        ])

        return_annotation = signature.return_annotation
        returns = (None if return_annotation is inspect.Signature.empty else
                   _convert_object_to_annotation(return_annotation, parent=func.parent))

        func.parameters = parameters
        func.returns = returns
