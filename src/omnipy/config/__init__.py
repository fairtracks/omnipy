from typing import TYPE_CHECKING

from omnipy.shared.enums.ui import TerminalOutputUserInterfaceType
from omnipy.util.publisher import DataPublisher

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter


class ConfigBase(DataPublisher):
    def default_repr_to_terminal_str(
        self,
        ui_type: TerminalOutputUserInterfaceType.Literals,
    ) -> str:
        from omnipy.components.json.models import JsonModel
        return JsonModel(self).default_repr_to_terminal_str(ui_type)

    def _repr_pretty_(self, p: 'RepresentationPrinter', cycle: bool) -> None:
        from omnipy.components.json.models import JsonModel
        JsonModel(self)._repr_pretty_(p, cycle)

    def _repr_html_(self) -> str:
        from omnipy.components.json.models import JsonModel
        return JsonModel(self)._repr_html_()
