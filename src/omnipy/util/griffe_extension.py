import inspect

import griffe

logger = griffe.get_logger('griffe_dyn_signature_specific_functions')


class UseDynamicSignatureForSpecificFunctions(griffe.Extension):
    def __init__(self, functions: list[str]) -> None:
        self.functions = functions

    def on_function_instance(self, *, func: griffe.Function, **kwargs) -> None:

        from _griffe.agents.inspector import _kind_map

        if func.path not in self.functions:
            return

        try:
            runtime_func = griffe.dynamic_import(func.path)
        except ImportError as error:
            logger.warning(f'Could not import {func.path}: {error}')
            return

        # Update default values modified by decorator.
        signature = inspect.signature(runtime_func)

        def _convert_parameter(parameter: inspect.Parameter) -> griffe.Parameter:
            name = parameter.name
            annotation = (None if parameter.annotation is inspect.Signature.empty else
                          parameter.annotation)
            kind: griffe.ParameterKind = _kind_map[parameter.kind]  # pyright: ignore
            if parameter.default is inspect.Signature.empty:
                default = None
            elif hasattr(parameter.default, '__name__'):
                # avoid repr containing chevrons and memory addresses
                default = parameter.default.__name__
            else:
                default = repr(parameter.default)
            return griffe.Parameter(name, annotation=annotation, kind=kind, default=default)

        parameters = griffe.Parameters(
            *[_convert_parameter(parameter) for parameter in signature.parameters.values()],)
        return_annotation = signature.return_annotation
        returns = (None if return_annotation is inspect.Signature.empty else return_annotation)

        func.parameters = parameters
        func.returns = returns
