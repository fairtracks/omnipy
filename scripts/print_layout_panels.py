from omnipy import JsonModel
from omnipy.data._display.config import (ConsoleColorSystem,
                                         DarkHighContrastColorStyles,
                                         DarkLowContrastColorStyles,
                                         PrettyPrinterLib,
                                         RecommendedColorStyles)
from omnipy.data._display.frame import Dimensions, Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.draft.base import DraftPanel, OutputConfig
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel

json = """[
         {
             "id": "0001",
             "type": "donut",
             "name": "Cake",
             "ppu": 0.55,
             "batters":
                 {
                     "batter":
                         [
                             {"id": "1001", "type": "Regular"},
                             {"id": "1002", "type": "Chocolate"},
                             {"id": "1003", "type": "Blueberry"},
                             {"id": "1004", "type": "Devil's Food"}
                         ]
                 },
             "topping":
                 [
                     {"id": "5001", "type": "None"},
                     {"id": "5002", "type": "Glazed"},
                     {"id": "5005", "type": "Sugar"},
                     {"id": "5007", "type": "Powdered Sugar"},
                     {"id": "5006", "type": "Chocolate with Sprinkles"},
                     {"id": "5003", "type": "Chocolate"},
                     {"id": "5004", "type": "Maple"}
                 ]
         },
         {
             "id": "0002",
             "type": "donut",
             "name": "Raised",
             "ppu": 0.55,
             "batters":
                 {
                     "batter":
                         [
                             {"id": "1001", "type": "Regular"}
                         ]
                 },
             "topping":
                 [
                     {"id": "5001", "type": "None"},
                     {"id": "5002", "type": "Glazed"},
                     {"id": "5005", "type": "Sugar"},
                     {"id": "5003", "type": "Chocolate"},
                     {"id": "5004", "type": "Maple"}
                 ]
         },
         {
             "id": "0003",
             "type": "donut",
             "name": "Old Fashioned",
             "ppu": 0.55,
             "batters":
                 {
                     "batter":
                         [
                             {"id": "1001", "type": "Regular"}
                         ]
                 },
             "topping":
                 [
                     {"id": "5001", "type": "None"},
                     {"id": "5002", "type": "Glazed"},
                     {"id": "5005", "type": "Sugar"},
                     {"id": "5003", "type": "Chocolate"},
                     {"id": "5004", "type": "Maple"}
                 ]
         },
         {
             "id": "0003",
             "type": "donut",
             "name": "Old Fashioned",
             "ppu": 0.55,
             "batters":
                 {
                     "batter":
                         [
                             {"id": "1001", "type": "Regular"},
                             {"id": "1002", "type": "Chocolate"}
                         ]
                 },
             "topping":
                 [
                     {"id": "5001", "type": "None"},
                     {"id": "5002", "type": "Glazed"},
                     {"id": "5003", "type": "Chocolate"},
                     {"id": "5004", "type": "Maple"}
                 ]
         }
     ]"""

tsv = """Username\tIdentifier\tFirst name\tLast name
booker12\t9012\tRachel\tBooker
grey07\t2070\tLaura\tGrey
johnson81\t4081\tCraig\tJohnson
jenkins46\t9346\tMary\tJenkins
smith79\t5079\tJamie\tSmith
"""

config = OutputConfig(
    console_color_system=ConsoleColorSystem.ANSI_RGB,
    color_style=RecommendedColorStyles.OMNIPY_SELENIZED_WHITE,
    transparent_background=False,
    language='python',
    debug_mode=False)
config1 = OutputConfig(
    console_color_system=ConsoleColorSystem.ANSI_RGB,
    color_style=DarkHighContrastColorStyles.TB16_BLACK_METAL_KHOLD,
    transparent_background=False,
    language='python',
    debug_mode=False,
    panel_title_at_top=False,
    tab_size=12,
)
config2 = OutputConfig(
    console_color_system=ConsoleColorSystem.ANSI_RGB,
    color_style=DarkHighContrastColorStyles.TB16_STELLA,
    transparent_background=False,
    language='python',
    debug_mode=False)
config3 = OutputConfig(
    console_color_system=ConsoleColorSystem.ANSI_RGB,
    color_style=RecommendedColorStyles.OMNIPY_SELENIZED_BLACK,
    transparent_background=True,
    language='python',
    debug_mode=False,
    pretty_printer=PrettyPrinterLib.RICH,
    tab_size=12)
config4 = OutputConfig(
    console_color_system=ConsoleColorSystem.ANSI_RGB,
    color_style=DarkLowContrastColorStyles.TB16_TAROT,
    transparent_background=False,
    language='json',
    debug_mode=False,
)


def print_with_config(json, tsv, config1, config2, config3, width, height):
    j = JsonModel()
    j.from_json(json)
    layout = Layout(
        first=DraftPanel(j[0], title='First panel', config=config1),
        second=ReflowedTextDraftPanel(json, title='Second panel', config=config2),
        third=ReflowedTextDraftPanel(tsv, title='Third panel', config=config3),
        fourth=DraftPanel(
            j[2], frame=Frame(Dimensions(30, 100)), title='Fourth panel', config=config3),
    )
    p = DraftPanel(layout, frame=Frame(Dimensions(width, height)), config=config3)
    print(p.render_next_stage().render_next_stage().colorized.terminal)
    return p


print_with_config(json, tsv, config1, config4, config3, 220, None)
print_with_config(json, tsv, config1, config4, config1, 220, 50)
print_with_config(json, tsv, config1, config4, config3, 196, 48)
print_with_config(json, tsv, config1, config4, config1, 195, 48)
print_with_config(json, tsv, config1, config4, config3, 80, 7)
print_with_config(json, tsv, config1, config4, config1, 80, 7)
print_with_config(json, tsv, config1, config4, config1, 80, 6)
print_with_config(json, tsv, config1, config4, config3, 40, 21)
print_with_config(json, tsv, config1, config4, config1, 40, 21)
print_with_config(json, tsv, config1, config4, config3, 40, 7)
print_with_config(json, tsv, config1, config4, config3, 40, 6)
print_with_config(json, tsv, config1, config4, config3, 30, 7)
print_with_config(json, tsv, config1, config4, config3, 30, 6)
print_with_config(json, tsv, config1, config4, config3, 22, 6)
