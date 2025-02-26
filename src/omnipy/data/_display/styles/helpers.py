from pydantic import BaseModel
from pygments.token import _TokenType  # noqa
from pygments.token import (Comment,
                            Error,
                            Escape,
                            Generic,
                            Keyword,
                            Name,
                            Number,
                            Operator,
                            Punctuation,
                            String,
                            Text,
                            Token)


class Base16Colors(BaseModel):
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


class Base16Theme(BaseModel):
    name: str
    author: str
    variant: str
    palette: Base16Colors


def get_styles_from_base16_colors(base16_colors: Base16Colors) -> dict[_TokenType, str]:
    return {
        Text: base16_colors.base05,
        Token: base16_colors.base05,
        Error: base16_colors.base08,
        Escape: base16_colors.base0C,
        Comment: 'italic ' + base16_colors.base03,
        Comment.Hashbang: 'bold',
        Comment.Special: 'bold',
        Comment.Preproc: base16_colors.base0C,
        Comment.PreprocFile: base16_colors.base0B,
        Punctuation: base16_colors.base05,
        Operator: base16_colors.base0C,
        Operator.Word: 'italic ' + base16_colors.base0C,
        Keyword: base16_colors.base0E,
        Keyword.Type: base16_colors.base0A,
        Keyword.Constant: base16_colors.base09,
        Keyword.Namespace: 'italic',
        Keyword.Pseudo: base16_colors.base0C,
        Name: base16_colors.base05,
        Name.Attribute: base16_colors.base0D,
        Name.Builtin: base16_colors.base0C,
        Name.Builtin.Pseudo: base16_colors.base08,
        Name.Class: base16_colors.base0A,
        Name.Constant: base16_colors.base09,
        Name.Decorator: 'italic ' + base16_colors.base0A,
        Name.Entity: base16_colors.base0C,
        Name.Exception: base16_colors.base08,
        Name.Function: base16_colors.base0D,
        Name.Label: base16_colors.base0D,
        Name.Namespace: 'italic ' + base16_colors.base05,
        Name.Tag: base16_colors.base0E,
        Name.Variable: base16_colors.base05,
        Name.Variable.Magic: base16_colors.base0C,
        Name.Property: base16_colors.base0D,
        Number: base16_colors.base09,
        String: base16_colors.base0B,
        String.Interpol: base16_colors.base05,
        String.Regex: base16_colors.base0C,
        String.Delimiter: base16_colors.base09,
        String.Heredoc: base16_colors.base0C,
        String.Symbol: base16_colors.base09,
        String.Doc: 'italic ' + base16_colors.base03,
        String.Escape: base16_colors.base0C,
        String.Affix: base16_colors.base0B,
        String.Backtick: base16_colors.base0C,
        String.Other: base16_colors.base0C,
        Generic: base16_colors.base05,
        Generic.Heading: 'bold ' + base16_colors.base0D,
        Generic.Subheading: base16_colors.base0D,
        Generic.Deleted: base16_colors.base08,
        Generic.Inserted: base16_colors.base0B,
        Generic.Changed: base16_colors.base0E,
        Generic.Error: base16_colors.base08,
        Generic.Emph: 'italic',
        Generic.Strong: 'bold',
        Generic.EmphStrong: 'italic bold',
        Generic.Prompt: base16_colors.base03,
        Generic.Output: base16_colors.base05,
        Generic.Traceback: base16_colors.base08,
    }
