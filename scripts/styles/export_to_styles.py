import os
from typing import NamedTuple

from inflection import underscore

from omnipy import JsonModel
from omnipy.data._display.config import (DarkHighContrastColorStyles,
                                         DarkLowContrastColorStyles,
                                         LightHighContrastColorStyles,
                                         LightLowContrastColorStyles,
                                         OutputConfig,
                                         RecommendedColorStyles)
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel import DraftMonospacedOutput, DraftOutput
from omnipy.data._display.pretty import pretty_repr_of_draft_output
from omnipy.data._display.styling import StylizedMonospacedOutput
from omnipy.data.typechecks import is_model_instance


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
        path='../../src/omnipy/data/_display/styling.py',
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
        for transparent_background in (True, False):
            transparency_label = 'default_bg' if transparent_background else 'style_bg'
            input_name = (f'{os.path.splitext(os.path.basename(input.path))[0]}'
                          f'_{input.data_type.__name__.lower()}')
            dirname = f'{input_name}/{underscore(style.group)}/{transparency_label}'
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            frame = Frame(Dimensions(165, None))
            config = OutputConfig(
                color_style=style.name,
                transparent_background=transparent_background,
                language=input.lexer,
                debug_mode=input.debug,
            )
            if is_model_instance(data):
                draft = DraftOutput(data, frame=frame, config=config)
                mono_draft = pretty_repr_of_draft_output(draft)
            else:
                mono_draft = DraftMonospacedOutput(data, frame=frame, config=config)

            output = StylizedMonospacedOutput(mono_draft)

            out_base_name = f"{input_name}_{style.name.replace('-', '_')}_{transparency_label}.html"
            out_file_name = f'{dirname}/{out_base_name}'
            print(out_file_name)

            with open(f'{out_file_name}', 'w') as output_file:
                output_file.write(output.colorized.html_page)
