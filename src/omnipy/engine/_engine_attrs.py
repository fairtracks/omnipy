"""Mixin for runtime publishers that hold registered engines as attributes."""

from typing import Any

from omnipy.engine.registry import engine_registry
from omnipy.shared.protocols.hub.runtime import IsRuntime
from omnipy.util.publisher import DataPublisher
import omnipy.util.pydantic as pyd


class EngineAttrsMixin(DataPublisher):
    """Allow registered engine names as extra attributes, loading plugin engines on first access.

    The built-in engines are declared fields. A plugin engine becomes an extra attribute when the
    runtime loads it, and reading the attribute before that loads it through the runtime. Assigning
    an attribute that is neither a field nor a registered engine name raises an error, as for any
    other config or runtime object.
    """

    class Config:
        """Pydantic settings allowing plugin engines as extra attributes."""

        extra = pyd.Extra.allow

    @pyd.root_validator(pre=True)
    def _only_registered_engines_as_extra_attrs(cls, values: dict[str, Any]) -> dict[str, Any]:
        for name in values:
            if name not in cls.__fields__ and not engine_registry.is_registered(name):
                raise ValueError(
                    f'"{name}" is neither an attribute of {cls.__name__} nor a registered engine'
                )
        return values

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_') or not engine_registry.is_registered(name):
            raise AttributeError(f'{type(self).__name__!r} object has no attribute {name!r}')

        # The back-link to the runtime is declared by the subclasses, as RuntimeEntryPublisher
        # already declares it for the runtime objects
        runtime: IsRuntime | None = getattr(self, '_back', None)
        if runtime is None:
            raise AttributeError(
                f'Engine "{name}" is not loaded, and {type(self).__name__} is not attached to a '
                'runtime that could load it'
            )

        runtime.load_engine(name)
        return self.__dict__[name]
