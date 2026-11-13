"""Shared configuration base types and display helpers."""

from collections.abc import Generator, Mapping
from typing import Any

from typing_extensions import override

from omnipy.shared.enums.display import SyntaxLanguageSpec
from omnipy.shared.enums.ui import TerminalOutputUserInterfaceType
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.publisher import DataPublisher
import omnipy.util.pydantic as pyd

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter

    from omnipy.components.json.models import JsonDictModel
    from omnipy.data._display.panel.draft.base import DraftPanel


MACHINE_LOCAL: dict[str, Any] = {'machine_local': True}
"""Field marker for config values that belong to the current machine or environment.

Use as ``pyd.Field(..., **MACHINE_LOCAL)`` for paths, detected values and other values that are
wrong or meaningless on another machine. The portable config export leaves them out.
"""


def _is_machine_local(field: Any) -> bool:
    return bool(field is not None and field.field_info.extra.get('machine_local'))


def _to_portable(value: object) -> object:
    if isinstance(value, ConfigBase):
        return value.to_portable_dict()
    if isinstance(value, Mapping):
        return {key: _to_portable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_portable(val) for val in value]
    return value


class ConfigBase(DataPublisher):
    """Base class for Omnipy configuration models.

    Secrets use ``pyd.SecretStr`` and are masked when the config is displayed. Values that belong
    to the current machine are marked with [`MACHINE_LOCAL`][omnipy.config.MACHINE_LOCAL]. Both
    are left out of the portable export, which can be applied to a config on another machine.
    """

    def to_portable_dict(self) -> dict[str, object]:
        """Return the config as JSON-compatible data, without secrets and machine-local values.

        The result can be sent to another machine, for example with a job that runs remotely,
        and applied there with
        [`update_from_portable_dict`][omnipy.config.ConfigBase.update_from_portable_dict].

        Returns:
            dict[str, object]: Nested dict of config values. Tuples become lists.
        """
        portable: dict[str, object] = {}
        for name in self._public_attr_names():
            if _is_machine_local(self.__class__.__fields__.get(name)):
                continue
            value = getattr(self, name)
            if isinstance(value, pyd.SecretStr):
                continue
            portable[name] = _to_portable(value)
        return portable

    def update_from_portable_dict(self, data: Mapping[str, object]) -> None:
        """Update this config in place from data made by ``to_portable_dict``.

        Nested configs are updated in place, so subscriptions to them stay intact. Mappings of
        configs, such as per-host HTTP settings, are updated key by key. Other values are
        assigned and validated as usual.

        Args:
            data: Portable config data, typically parsed from JSON.

        Raises:
            AttributeError: If ``data`` contains a name that is not an attribute of this config.
        """
        for name, value in data.items():
            current = getattr(self, name)
            if isinstance(current, ConfigBase) and isinstance(value, Mapping):
                current.update_from_portable_dict(value)
            elif (
                isinstance(current, Mapping)
                and isinstance(value, Mapping)
                and all(isinstance(val, Mapping) for val in value.values())
                and all(isinstance(val, ConfigBase) for val in current.values())
            ):
                for key, val in value.items():
                    current[key].update_from_portable_dict(val)
            else:
                setattr(self, name, value)

    def _iter(self, **kwargs: Any) -> Generator[tuple[str, Any], None, None]:  # type: ignore[override]
        for key, val in super()._iter(**kwargs):
            if isinstance(val, pyd.SecretStr):
                # Masked text, so that configs with secrets can be displayed as JSON models
                yield key, str(val)
            else:
                yield key, val

    def as_model(self) -> 'JsonDictModel':
        """Return a JSON model representation of the current configuration.

        Allows the configuration object to be serialized, displayed, and
        inspected using the same rendering pipeline as any other Omnipy
        model.  The returned ``ConfigModel`` subclass also customizes the
        default display panel to use JSON5 syntax.

        Returns:
            JsonDictModel: A JSON model view of this configuration instance.
        """
        from omnipy.components.json.models import JsonDictModel

        class ConfigModel(JsonDictModel):
            @override
            def _default_panel(self, **kwargs) -> 'DraftPanel':
                kwargs_copy = kwargs.copy()
                kwargs_copy['syntax'] = SyntaxLanguageSpec.JSON5
                return self._full(**kwargs_copy)

        return ConfigModel(self)  # pyright: ignore [reportReturnType]

    def default_repr_to_terminal_str(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals,
    ) -> str:
        return self.as_model().default_repr_to_terminal_str(ui_type)

    def _repr_pretty_(self, p: 'RepresentationPrinter', cycle: bool) -> None:
        self.as_model()._repr_pretty_(p, cycle)

    def _ipython_display_(self) -> None:
        self.as_model()._ipython_display_()

    def __str__(self):
        return repr(self)
