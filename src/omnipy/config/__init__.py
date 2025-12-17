from typing import TYPE_CHECKING

from typing_extensions import override

from omnipy.shared.enums.display import SyntaxLanguage
from omnipy.shared.enums.ui import TerminalOutputUserInterfaceType
from omnipy.util.publisher import DataPublisher

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter

    from omnipy.components.json.models import JsonDictModel
    from omnipy.data._display.panel.draft.base import DraftPanel


class ConfigBase(DataPublisher):
    def as_model(self) -> 'JsonDictModel':
        from omnipy.components.json.models import JsonDictModel

        class ConfigModel(JsonDictModel):
            @override
            def _default_panel(self, **kwargs) -> 'DraftPanel':
                kwargs_copy = kwargs.copy()
                kwargs_copy['syntax'] = SyntaxLanguage.JSON5
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
