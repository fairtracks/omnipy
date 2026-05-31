from omnipy.components.tables.models import JsonScalarColumnModel
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout.base import Layout
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanelLayout, DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel


def test_nested_panels_with_cropped_column_models() -> None:
    # Pinning down a bug that was extremely hard to pin down
    """Test nested panels with cropped column models."""
    panel = ResizedLayoutDraftPanel(
        DimensionsAwareDraftPanelLayout(**Layout({
            'inner':
                DraftPanel(
                    Layout({
                        str(i):
                            DraftPanel(
                                JsonScalarColumnModel(range(i, i + 5)),
                                frame=Frame(dims=Dimensions(width=1, height=None)),
                                config=OutputConfig(use_min_crop_width=True)) for i in range(3)
                    }),
                    frame=Frame(dims=Dimensions(width=13, height=None)),
                )
        })))
    assert '…' in panel.render_next_stage().colorized.terminal
