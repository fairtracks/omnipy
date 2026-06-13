from omnipy.data._display.panel.draft.base import DraftPanel


def render_panel_to_plain_terminal(panel: DraftPanel) -> str:
    return panel.render_next_stage().render_next_stage().plain.terminal
