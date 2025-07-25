import os
from typing import NamedTuple

from inflection import underscore

from omnipy import JsonModel
from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
from omnipy.data._display.text.pretty import pretty_repr_of_draft_output
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums.colorstyles import (DarkHighContrastColorStyles,
                                             DarkLowContrastColorStyles,
                                             LightHighContrastColorStyles,
                                             LightLowContrastColorStyles,
                                             RecommendedColorStyles)


class Inputs(NamedTuple):
    path: str
    lexer: str
    data_type: type
    debug: bool


class Styles(NamedTuple):
    group: str
    name: str


inputs = [
    Inputs(path='donuts.json', lexer='json', data_type=str, debug=False),
    Inputs(path='donuts.json', lexer='python', data_type=JsonModel, debug=True),
    Inputs(
        path='../../src/omnipy/data/_display/panel/styling/output.py',
        lexer='python',
        data_type=str,
        debug=False),
]

styles = []
for style_enum in (RecommendedColorStyles,
                   DarkHighContrastColorStyles,
                   DarkLowContrastColorStyles,
                   LightHighContrastColorStyles,
                   LightLowContrastColorStyles):
    for style_name in style_enum:
        styles.append(Styles(group=style_enum.__name__[:-len('ColorStyles')], name=style_name))

for input in inputs:
    data: str | JsonModel
    with open(input.path) as input_file:
        if input.data_type is str:
            data = input_file.read()
        else:
            assert input.data_type is JsonModel
            data = JsonModel()
            data.from_json(input_file.read())

    for style in styles:
        # print(style)
        for solid_background in (True, False):
            transparency_label = 'default_bg' if solid_background else 'style_bg'
            input_name = (f'{os.path.splitext(os.path.basename(input.path))[0]}'
                          f'_{input.data_type.__name__.lower()}')
            dirname = f'{input_name}/{underscore(style.group)}/{transparency_label}'
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            frame = Frame(Dimensions(165, None))
            config = OutputConfig(
                style=style.name,
                bg=solid_background,
                lang=input.lexer,
                debug=input.debug,
            )
            if is_model_instance(data):
                draft_panel = DraftPanel(data, frame=frame, config=config)
                reflowed_text_panel = pretty_repr_of_draft_output(draft_panel)
            else:
                reflowed_text_panel = ReflowedTextDraftPanel(data, frame=frame, config=config)

            stylized_text_panel = SyntaxStylizedTextPanel(reflowed_text_panel)

            out_base_name = f"{input_name}_{style.name.replace('-', '_')}_{transparency_label}.html"
            out_file_name = f'{dirname}/{out_base_name}'
            print(out_file_name)

            with open(f'{out_file_name}', 'w') as output_file:
                output_file.write(stylized_text_panel.colorized.html_page)
