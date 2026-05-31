"""Runtime configuration and the global Omnipy runtime singleton.

The runtime wires together configuration, engines, serializers, registries,
and user-interface integration for the current process. Most user code works
with the module-level ``runtime`` object rather than constructing a
``Runtime`` manually.

Attributes:
    runtime: Global ``Runtime`` singleton for the current Python process. It
        owns shared configuration and runtime objects, and it auto-initializes
        UI integration outside the test environment.
"""

from typing import Any, cast

from omnipy.components.prefect.engine.prefect import PrefectEngine
from omnipy.compute._job import JobBase
from omnipy.config import ConfigBase
from omnipy.config.data import DataConfig
from omnipy.config.engine import EngineConfig
from omnipy.config.job import JobConfig
from omnipy.config.root_log import RootLogConfig
from omnipy.data._data_class_creator import DataClassBase
from omnipy.data.serializer import SerializerRegistry
from omnipy.engine.local import LocalRunner
from omnipy.hub._registry import RunStateRegistry
from omnipy.hub.log._root_log import RootLogObjects
from omnipy.hub.ui import detect_and_setup_user_interface
from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.enums.ui import UserInterfaceType
from omnipy.shared.protocols.compute.job_creator import IsJobConfigHolder, IsJobCreator
from omnipy.shared.protocols.config import (IsDataConfig,
                                            IsEngineConfig,
                                            IsJobConfig,
                                            IsJobRunnerConfig,
                                            IsRootLogConfig)
from omnipy.shared.protocols.data import IsDataClassCreator, IsReactiveObjects, IsSerializerRegistry
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.shared.protocols.hub.runtime import (IsRootLogObjects,
                                                 IsRuntime,
                                                 IsRuntimeConfig,
                                                 IsRuntimeObjects)
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import called_from_omnipy_tests
from omnipy.util.publisher import DataPublisher, RuntimeEntryPublisher
import omnipy.util.pydantic as pyd


def _job_creator_factory() -> IsJobCreator:
    """Return the process-global job creator used by runtimes.

    Returns:
        IsJobCreator: Shared job creator owned by ``JobBase``.
    """

    return JobBase.job_creator


def _job_config_factory() -> IsJobConfig:
    """Return the active job configuration from the shared job creator.

    Returns:
        IsJobConfig: Runtime job configuration object.
    """

    return _job_creator_factory().config


def _data_class_creator_factory() -> IsDataClassCreator:
    """Return the process-global data class creator used by runtimes.

    Returns:
        IsDataClassCreator: Shared data class creator owned by
            ``DataClassBase``.
    """

    return DataClassBase.data_class_creator


def _data_config_factory() -> IsDataConfig:
    """Return the active data configuration from the shared data creator.

    Returns:
        IsDataConfig: Runtime data configuration object.
    """

    return _data_class_creator_factory().config


class RuntimeConfig(RuntimeEntryPublisher, ConfigBase):
    """Configuration tree owned by a ``Runtime`` instance.

    Attributes:
        data: Data-related runtime settings.
        engine: Engine selection and per-engine configuration.
        job: Job creation and execution settings.
        root_log: Root logger integration settings.

    """

    data: IsDataConfig = pyd.Field(default_factory=_data_config_factory)
    engine: IsEngineConfig = pyd.Field(default_factory=EngineConfig)
    job: IsJobConfig = pyd.Field(default_factory=_job_config_factory)
    root_log: IsRootLogConfig = pyd.Field(default_factory=RootLogConfig)

    def reset_to_defaults(self) -> None:
        """{{ISRUNTIMECONFIG_RESET_TO_DEFAULTS_SUMMARY}}

        {{ISRUNTIMECONFIG_RESET_TO_DEFAULTS_DETAILS}}"""

        prev_back = self._back
        self._back = None

        self.data = cast(IsDataConfig, DataConfig())
        self.engine = cast(IsEngineConfig, EngineConfig())
        self.job = cast(IsJobConfig, JobConfig())
        self.root_log = cast(IsRootLogConfig, RootLogConfig())

        self._back = prev_back
        if self._back is not None:
            self._back.reset_subscriptions()


class RuntimeObjects(RuntimeEntryPublisher, DataPublisher):
    """Concrete services and registries owned by a ``Runtime`` instance.

    Attributes:
        job_creator: Shared job creator configured by ``RuntimeConfig.job``.
        data_class_creator: Shared data creator configured by
            ``RuntimeConfig.data``.
        reactive: Optional UI-reactive helper objects for notebook contexts.
        local: Local execution engine.
        prefect: Prefect execution engine.
        registry: Runtime run-state registry.
        serializers: Dataset serializer registry.
        root_log: Root logging integration objects.

    """

    job_creator: IsJobConfigHolder = pyd.Field(default_factory=_job_creator_factory)
    data_class_creator: IsDataClassCreator = pyd.Field(default_factory=_data_class_creator_factory)
    reactive: IsReactiveObjects | None = None
    local: IsEngine = pyd.Field(default_factory=LocalRunner)
    prefect: IsEngine = pyd.Field(default_factory=PrefectEngine)
    registry: IsRunStateRegistry = pyd.Field(default_factory=RunStateRegistry)
    serializers: IsSerializerRegistry = pyd.Field(default_factory=SerializerRegistry)
    root_log: IsRootLogObjects = pyd.Field(default_factory=RootLogObjects)

    def setup_reactive(self, ui_type: UserInterfaceType.Literals) -> None:
        """{{ISRUNTIMEOBJECTS_SETUP_REACTIVE_SUMMARY}}

        {{ISRUNTIMEOBJECTS_SETUP_REACTIVE_DETAILS}}"""

        if UserInterfaceType.is_jupyter_in_browser(ui_type):
            from omnipy.data._display.integrations.jupyter.helpers import ReactiveObjects

            if self.reactive is None:
                self.reactive = ReactiveObjects()
        else:
            if self.reactive is not None:
                self.reactive = None


class Runtime(DataPublisher):
    """Application-level runtime object coordinating shared Omnipy services.

    A ``Runtime`` keeps configuration and runtime objects in sync, selects the
    active execution engine, and initializes display-related integration for
    the current environment. Most applications should use the module-level
    ``runtime`` singleton.

    Attributes:
        config: Runtime configuration object.
        objects: Runtime service and registry container.

    """

    config: IsRuntimeConfig = pyd.Field(default_factory=RuntimeConfig)
    objects: IsRuntimeObjects = pyd.Field(default_factory=RuntimeObjects)

    def __init__(self, **data: Any) -> None:
        """Initialize runtime data, UI integration, and subscriptions.

        Args:
            **data: Optional initialization data passed to ``DataPublisher``.
        """

        super().__init__(**data)
        detect_and_setup_user_interface(self)
        self.reset_subscriptions()

    def reset_subscriptions(self) -> None:
        """{{ISRUNTIME_RESET_SUBSCRIPTIONS_SUMMARY}}

        {{ISRUNTIME_RESET_SUBSCRIPTIONS_DETAILS}}"""

        self.reset_backlinks()

        self.config.unsubscribe_all()
        self.objects.unsubscribe_all()

        # Makes sure that the config references in the runtime objects always refer to the related
        # config in runtime, even when:
        #
        # 1. The runtime config is replaced with a new config object, or
        # 2. The runtime object is replaced with a new runtime object, or
        # 3. Both of the above
        #
        # This might e.g. happen due to the use of  mock objects for testing, or if the config is
        # reloaded from a file.

        self.config.subscribe_attr('data', self.objects.data_class_creator.set_config)
        self.config.subscribe_attr('job', self.objects.job_creator.set_config)
        self.config.subscribe_attr('root_log', self.objects.root_log.set_config)

        self.config.data.ui.subscribe_attr('detected_type', self.objects.setup_reactive)

        if UserInterfaceType.is_jupyter_in_browser(self.config.data.ui.detected_type):
            assert self.objects.reactive is not None
            self.config.data.ui.subscribe_attr('jupyter',
                                               self.objects.reactive.jupyter_ui_config.set)
            self.config.data.ui.subscribe_attr('text', self.objects.reactive.text_config.set)
            self.config.data.ui.subscribe_attr('layout', self.objects.reactive.layout_config.set)

        self.config.engine.subscribe_attr('local', self.objects.local.set_config)
        self.config.engine.subscribe_attr('prefect', self.objects.prefect.set_config)

        self.objects.subscribe_attr(
            'reactive',
            self.objects.data_class_creator.set_reactive_objects,
        )

        # Makes sure that the registry references in the job runners always refer to the registry
        # object in runtime, even when one or both of the objects are replaced with new objects.
        self.objects.subscribe_attr('registry', self.objects.local.set_registry)
        self.objects.subscribe_attr('registry', self.objects.prefect.set_registry)

        # Makes sure that the engine used by the job creator is always the one specified in the
        # 'engine' config item in runtime
        self.config.engine.subscribe_attr('local', self._update_job_creator_engine)
        self.config.engine.subscribe_attr('prefect', self._update_job_creator_engine)
        self.config.engine.subscribe_attr('choice', self._update_job_creator_engine)

        # Makes sure that the local and prefect engine configs are always reloaded when the local
        # or prefect engine objects are replaced with new engine objects. This is necessary because
        # the `get_config_cls()` method of the engine objects define the classes of the respective
        # engine config objects to be used. If an engine object is replaced with a new engine that
        # require a different engine config class than is currently used, the config object will be
        # replaced with a new default config object of the correct type.
        self.objects.subscribe_attr('local', self._update_local_runner_config)
        self.objects.subscribe_attr('prefect', self._update_prefect_engine_config)

    def reset_backlinks(self) -> None:
        """Set parent backlinks from runtime sub-objects to this runtime."""

        self.config._back = self  # type: ignore[attr-defined]
        self.objects._back = self  # type: ignore[attr-defined]

    def _get_engine_config(self, choice: EngineChoice.Literals) -> IsEngineConfig:
        """Return the engine configuration object for a selected engine.

        Args:
            choice: Engine identifier whose configuration should be returned.

        Returns:
            IsEngineConfig: Configuration object for the selected engine.

        Raises:
            AttributeError: If ``choice`` does not exist on ``config.engine``.
        """

        return getattr(self.config.engine, choice)

    def _set_engine_config(
        self,
        choice: EngineChoice.Literals,
        engine_config: IsJobRunnerConfig,
    ) -> None:
        """Set the configuration object for a selected engine.

        Args:
            choice: Engine identifier whose configuration should be updated.
            engine_config: New engine configuration object.

        Raises:
            AttributeError: If ``choice`` does not exist on ``config.engine``.
        """

        setattr(self.config.engine, choice, engine_config)

    def _get_engine(self, choice: EngineChoice.Literals) -> IsEngine:
        """Return the engine object for a selected engine choice.

        Args:
            choice: Engine identifier whose runtime engine should be returned.

        Returns:
            IsEngine: Runtime engine object for ``choice``.

        Raises:
            AttributeError: If ``choice`` does not exist on ``objects``.
        """

        return getattr(self.objects, choice)

    def _new_engine_config_if_new_cls(
        self,
        engine: IsEngine,
        choice: EngineChoice.Literals,
    ) -> None:
        """Replace engine config when an engine requires a new config class.

        Args:
            engine: Engine instance to inspect for config class changes.
            choice: Engine identifier whose config may need replacement.
        """

        # TODO: when parsing config from file is implemented, make sure that the new engine
        #       config classes here reparse the config files
        engine_config_cls = engine.get_config_cls()
        if self._get_engine_config(choice).__class__ is not engine_config_cls:
            self._set_engine_config(choice, engine_config_cls())

    def _update_local_runner_config(self, local_runner: IsEngine) -> None:
        """Refresh local engine config when the local engine object changes.

        Args:
            local_runner: New local engine instance.
        """

        self._new_engine_config_if_new_cls(local_runner, EngineChoice.LOCAL)

    def _update_prefect_engine_config(self, prefect_engine: IsEngine) -> None:
        """Refresh Prefect engine config when the Prefect engine changes.

        Args:
            prefect_engine: New Prefect engine instance.
        """

        self._new_engine_config_if_new_cls(prefect_engine, EngineChoice.PREFECT)

    def _update_job_creator_engine(self, _item_changed: Any) -> None:
        """Sync the job creator with the currently selected runtime engine.

        Args:
            _item_changed: Subscription payload for the triggering change.

        Raises:
            AttributeError: If the configured engine choice has no matching
                runtime engine object.
        """

        self.objects.job_creator.set_engine(self._get_engine(self.config.engine.choice))


if TYPE_CHECKING:
    runtime: 'IsRuntime' = Runtime()
else:
    runtime: 'IsRuntime | None' = None if called_from_omnipy_tests() else Runtime()
