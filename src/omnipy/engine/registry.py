"""Registry of the job runner engines available to the runtime.

The built-in engines (``local`` and ``prefect``) are always registered. Plugin packages add
engines by declaring an entry point in the ``omnipy.engines`` group, where the entry point name
is the engine name and the value points at the engine class::

    [project.entry-points."omnipy.engines"]
    tes = "omnipy_ga4gh_sdk.engine:TesEngine"

Only the entry point names are read when the registry is first used. A plugin module is imported
the first time its engine class is needed, for example when the engine is chosen in
``runtime.config.engine.choice``. A plugin may also register its engine explicitly with
[`EngineRegistry.register`][omnipy.engine.registry.EngineRegistry.register]; registering the same
class twice does nothing.
"""

from importlib.metadata import entry_points, EntryPoint
import logging

from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.protocols.engine.base import IsEngine

ENGINE_ENTRY_POINT_GROUP = 'omnipy.engines'

_BUILTIN_ENGINES: dict[str, str] = {
    EngineChoice.LOCAL: 'omnipy.engine.local:LocalRunner',
    EngineChoice.PREFECT: 'omnipy.components.prefect.engine.prefect:PrefectEngine',
}

BUILTIN_ENGINE_NAMES: tuple[str, ...] = tuple(_BUILTIN_ENGINES)

_logger = logging.getLogger(__name__)


def _is_valid_engine_name(name: str) -> bool:
    return name.isidentifier() and not name.startswith('_')


def _import_path(engine_cls: type) -> str:
    return f'{engine_cls.__module__}:{engine_cls.__qualname__}'


class EngineRegistry:
    """Names and classes of the engines that the runtime can load.

    Each engine is stored either as an entry point that has not been loaded yet, or as the
    engine class itself once it has been loaded or registered explicitly.
    """

    def __init__(self) -> None:
        self._engines: dict[str, EntryPoint | type[IsEngine]] = {}
        self._discovered = False
        self._add_builtin_engines()

    def _add_builtin_engines(self) -> None:
        for name, value in _BUILTIN_ENGINES.items():
            self._engines[name] = EntryPoint(name, value, ENGINE_ENTRY_POINT_GROUP)

    def _discover(self) -> None:
        if self._discovered:
            return
        self._discovered = True

        for entry_point in entry_points(group=ENGINE_ENTRY_POINT_GROUP):
            name = entry_point.name
            if not _is_valid_engine_name(name):
                _logger.warning(
                    f'Ignoring engine entry point "{name}" ({entry_point.value}): engine names '
                    'must be valid Python identifiers not starting with an underscore'
                )
            elif name in self._engines:
                if self._import_path_of(name) != entry_point.value:
                    _logger.warning(
                        f'Ignoring engine entry point "{name}" ({entry_point.value}): an engine '
                        f'with this name is already registered ({self._import_path_of(name)})'
                    )
            else:
                self._engines[name] = entry_point

    def _import_path_of(self, name: str) -> str:
        engine = self._engines[name]
        if isinstance(engine, EntryPoint):
            return engine.value
        return _import_path(engine)

    def names(self) -> tuple[str, ...]:
        """Return the names of all registered engines, built-in engines first.

        Returns:
            tuple[str, ...]: Engine names, including plugin engines that are not loaded yet.
        """
        self._discover()
        return tuple(self._engines)

    def is_registered(self, name: str) -> bool:
        """Return whether an engine with the given name is registered.

        Args:
            name: Engine name to look up.

        Returns:
            bool: ``True`` if the engine is registered, whether loaded or not.
        """
        return name in self.names()

    def check_name(self, name: str) -> None:
        """Raise an error naming the registered engines if ``name`` is not one of them.

        Args:
            name: Engine name to check.

        Raises:
            ValueError: If no engine with this name is registered.
        """
        if not self.is_registered(name):
            installed = ', '.join(f'"{name}"' for name in self.names())
            raise ValueError(f'Unknown engine "{name}". Registered engines: {installed}')

    def is_loaded(self, name: str) -> bool:
        """Return whether the class of a registered engine has been loaded.

        Args:
            name: Name of a registered engine.

        Returns:
            bool: ``True`` if the engine class has been imported or registered explicitly.
        """
        self.check_name(name)
        return not isinstance(self._engines[name], EntryPoint)

    def get_engine_cls(self, name: str) -> type[IsEngine]:
        """Return the engine class for a registered engine, importing it if needed.

        Args:
            name: Name of a registered engine.

        Returns:
            type[IsEngine]: The engine class.

        Raises:
            ValueError: If no engine with this name is registered.
        """
        self.check_name(name)
        engine = self._engines[name]
        if isinstance(engine, EntryPoint):
            loaded = self._engines[name]
            engine_cls = engine.load()
            # Importing the plugin module may already have registered the class explicitly
            if self._engines[name] is loaded:
                self._engines[name] = engine_cls
            return self._engines[name]  # type: ignore[return-value]
        return engine

    def register(self, name: str, engine_cls: type[IsEngine]) -> None:
        """Register an engine class under a name.

        Registering the same class again, or a class matching an already declared entry point,
        does nothing.

        Args:
            name: Engine name, used for ``runtime.config.engine.choice`` and as the attribute name
                in ``runtime.config.engine`` and ``runtime.objects``.
            engine_cls: Engine class to register.

        Raises:
            ValueError: If the name is not a valid engine name, or if a different engine is
                already registered under it.
        """
        if not _is_valid_engine_name(name):
            raise ValueError(
                f'Invalid engine name "{name}": engine names must be valid Python identifiers '
                'not starting with an underscore'
            )

        self._discover()
        if name in self._engines:
            existing = self._engines[name]
            if existing is engine_cls:
                return
            if isinstance(existing, EntryPoint) and existing.value == _import_path(engine_cls):
                self._engines[name] = engine_cls
                return
            raise ValueError(
                f'Cannot register engine "{name}" ({_import_path(engine_cls)}): an engine with '
                f'this name is already registered ({self._import_path_of(name)})'
            )

        self._engines[name] = engine_cls

    def refresh(self) -> None:
        """Forget plugin engines and discover the installed entry points again.

        Mainly useful for testing. Explicitly registered engines are forgotten too.
        """
        self._engines.clear()
        self._discovered = False
        self._add_builtin_engines()


engine_registry = EngineRegistry()
"""Process-wide engine registry used by the runtime."""
