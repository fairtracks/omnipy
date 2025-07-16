import pygments.token
from pygments.token import Token

import omnipy.util._pydantic as pyd

Base16 = Token.Base16

# See Chris Kempson's Base16 framework
# https://github.com/chriskempson/base16/blob/main/styling.md
Base16.DefaultBackground
Base16.LighterBackground
Base16.SelectionBackground
Base16.LineHighlight
Base16.DarkForeground
Base16.DefaultForeground
Base16.LightForeground
Base16.LightBackground
Base16.Variables
Base16.Integers
Base16.Classes
Base16.Strings
Base16.Support
Base16.Functions
Base16.Keywords
Base16.Deprecated


class Base16Colors(pyd.BaseModel):
    base00: str
    base01: str
    base02: str
    base03: str
    base04: str
    base05: str
    base06: str
    base07: str
    base08: str
    base09: str
    base0A: str
    base0B: str
    base0C: str
    base0D: str
    base0E: str
    base0F: str


class Base16Theme(pyd.BaseModel):
    name: str
    author: str
    variant: str
    palette: Base16Colors


def get_styles_from_base16_colors(
        base16_colors: Base16Colors) -> dict[pygments.token._TokenType, str]:
    return {
        pygments.token.Text: base16_colors.base05,
        pygments.token.Token: base16_colors.base05,
        pygments.token.Error: base16_colors.base08,
        pygments.token.Escape: base16_colors.base0C,
        pygments.token.Comment: 'italic ' + base16_colors.base03,
        pygments.token.Comment.Hashbang: 'bold',
        pygments.token.Comment.Special: 'bold',
        pygments.token.Comment.Preproc: base16_colors.base0C,
        pygments.token.Comment.PreprocFile: base16_colors.base0B,
        pygments.token.Punctuation: base16_colors.base05,
        pygments.token.Operator: base16_colors.base0C,
        pygments.token.Operator.Word: 'italic ' + base16_colors.base0C,
        pygments.token.Keyword: base16_colors.base0E,
        pygments.token.Keyword.Type: base16_colors.base0A,
        pygments.token.Keyword.Constant: 'bold ' + base16_colors.base0A,
        pygments.token.Keyword.Namespace: 'italic',
        pygments.token.Keyword.Pseudo: base16_colors.base0C,
        pygments.token.Name: base16_colors.base05,
        pygments.token.Name.Attribute: base16_colors.base0D,
        pygments.token.Name.Builtin: base16_colors.base0C,
        pygments.token.Name.Builtin.Pseudo: base16_colors.base08,
        pygments.token.Name.Class: base16_colors.base0A,
        pygments.token.Name.Constant: base16_colors.base09,
        pygments.token.Name.Decorator: 'italic ' + base16_colors.base0A,
        pygments.token.Name.Entity: base16_colors.base0C,
        pygments.token.Name.Exception: base16_colors.base08,
        pygments.token.Name.Function: base16_colors.base0D,
        pygments.token.Name.Label: base16_colors.base0D,
        pygments.token.Name.Namespace: 'italic ' + base16_colors.base05,
        pygments.token.Name.Tag: base16_colors.base0E,
        pygments.token.Name.Variable: base16_colors.base05,
        pygments.token.Name.Variable.Magic: base16_colors.base0C,
        pygments.token.Name.Property: base16_colors.base0D,
        pygments.token.Number: base16_colors.base09,
        pygments.token.String: base16_colors.base0B,
        pygments.token.String.Interpol: base16_colors.base05,
        pygments.token.String.Regex: base16_colors.base0C,
        pygments.token.String.Delimiter: base16_colors.base09,
        pygments.token.String.Heredoc: base16_colors.base0C,
        pygments.token.String.Symbol: base16_colors.base09,
        pygments.token.String.Doc: 'italic ' + base16_colors.base03,
        pygments.token.String.Escape: base16_colors.base0C,
        pygments.token.String.Affix: base16_colors.base0B,
        pygments.token.String.Backtick: base16_colors.base0C,
        pygments.token.String.Other: base16_colors.base0C,
        pygments.token.Generic: base16_colors.base05,
        pygments.token.Generic.Heading: 'bold ' + base16_colors.base0D,
        pygments.token.Generic.Subheading: 'italic ' + base16_colors.base0A,
        pygments.token.Generic.Deleted: base16_colors.base08,
        pygments.token.Generic.Inserted: base16_colors.base0B,
        pygments.token.Generic.Changed: base16_colors.base0E,
        pygments.token.Generic.Error: base16_colors.base08,
        pygments.token.Generic.Emph: 'italic',
        pygments.token.Generic.Strong: 'bold',
        pygments.token.Generic.EmphStrong: 'italic bold',
        pygments.token.Generic.Prompt: base16_colors.base03,
        pygments.token.Generic.Output: base16_colors.base05,
        pygments.token.Generic.Traceback: base16_colors.base08,
        Base16.DefaultBackground: base16_colors.base00,
        Base16.LighterBackground: base16_colors.base01,
        Base16.SelectionBackground: base16_colors.base02,
        Base16.LineHighlight: base16_colors.base03,
        Base16.DarkForeground: base16_colors.base04,
        Base16.DefaultForeground: base16_colors.base05,
        Base16.LightForeground: base16_colors.base06,
        Base16.LightBackground: base16_colors.base07,
        Base16.Variables: base16_colors.base0D,
        Base16.Integers: base16_colors.base09,
        Base16.Classes: base16_colors.base0A,
        Base16.Strings: base16_colors.base0B,
        Base16.Support: base16_colors.base0C,
        Base16.Functions: base16_colors.base0D,
        Base16.Keywords: base16_colors.base0E,
        Base16.Deprecated: base16_colors.base08,
    }
