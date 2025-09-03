from typing import TYPE_CHECKING

from omnipy.shared.enums.display import SyntaxLanguage
from omnipy.shared.enums.ui import TerminalOutputUserInterfaceType
from omnipy.util.publisher import DataPublisher

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter

    from omnipy.data._display.panel.draft.base import DraftPanel
    from omnipy.data._mixins.display import ModelDisplayMixin


class ConfigBase(DataPublisher):
    def _create_config_model(self) -> 'ModelDisplayMixin':
        from omnipy.components.json.models import JsonModel

        class ConfigModel(JsonModel):
            def _default_panel(self, **kwargs) -> 'DraftPanel':
                kwargs_copy = kwargs.copy()
                kwargs_copy['syntax'] = SyntaxLanguage.JSON
                return self._full(**kwargs_copy)

        return ConfigModel(self)

    def default_repr_to_terminal_str(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals,
    ) -> str:
        return self._create_config_model().default_repr_to_terminal_str(ui_type)

    def _repr_pretty_(self, p: 'RepresentationPrinter', cycle: bool) -> None:
        self._create_config_model()._repr_pretty_(p, cycle)

    def _ipython_display_(self) -> None:
        self._create_config_model()._ipython_display_()

    def __str__(self):
        return repr(self)
