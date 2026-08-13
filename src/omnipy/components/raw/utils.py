import re


class RegexMatch:
    """Wrapper to make regex patterns matchable using the `match` syntax.

    Examples:
        >>> import omnipy as om
        >>> from typing import Literal

        >>> class MyMapper(om.ConverterModel[str, Literal['yes', 'no']]):
        ...     @classmethod
        ...     def _convert(cls, data: str) -> Literal['yes', 'no']:
        ...         match RegexMatch(data.lower()):
        ...             case r'ye(s|ah?)':
        ...                 return 'yes'
        ...             case r'no(pe)?':
        ...                 return 'no'
        ...             case _:
        ...                 raise ValueError(f'Invalid value: {data}')

        >>> assert MyMapper('yea').to_data() == 'yes'
    """
    def __init__(self, text: str):
        self._text = text

    def __eq__(self, pattern: re.Pattern[str]) -> bool:  # type: ignore[override]
        return re.search(pattern, self._text) is not None
