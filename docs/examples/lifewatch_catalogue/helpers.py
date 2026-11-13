"""Normalisation of field values in the ES source of catalogue records."""


def single_value(value: object) -> object:
    """ES returns a field with one value as the value itself, and with several as a list."""
    return value[0] if isinstance(value, list) and len(value) == 1 else value


def as_list(value: object) -> object:
    return [] if value in (None, '') else value if isinstance(value, list) else [value]


def default_text(value: object) -> object:
    """Return the default text of a multilingual field, e.g. `{'default': 'Marine VRE'}`."""
    value = single_value(value)
    return value.get('default') if isinstance(value, dict) else value


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def codelist_value(value: str) -> str:
    """Strip the '--' suffix of topic and category codelist values, e.g. 'data analysis--'."""
    return value.removesuffix('--')


def contained_service_name(value: str) -> str:
    """Return the name of a contained service, given as 'name|description|url'."""
    return value.split('|')[0]
