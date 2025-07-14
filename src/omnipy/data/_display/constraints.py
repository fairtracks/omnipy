import omnipy.util._pydantic as pyd


@pyd.dataclass(
    kw_only=True,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class Constraints:
    """Constraints for display of content."""

    max_inline_container_width_incl: pyd.NonNegativeInt | None = None
    """
    Limit of character width for any Python container (e.g. list, tuple, dict, object) per line.
    This limit includes the container end characters (brackets, curly brackets, ...)
    Used internally in DevtoolsPrettyPrinter to manage the `simple_cutoff` parameter.
    """

    max_inline_list_or_dict_width_excl: pyd.NonNegativeInt | None = None
    """
    Limit of character width for any Python container (e.g. list, tuple, dict, object) per line.
    This limit does not have to inlude the container end characters (brackets, curly brackets, ...)
    Used internally in CompactjsonPrettyPrinter to manage the `max_inline_length` parameter.
    """


class ConstraintsSatisfaction:
    def __init__(self,
                 constraints: Constraints,
                 *,
                 max_inline_container_width_incl: int | None = None,
                 max_inline_list_or_dict_width_excl: int | None = None) -> None:

        self._max_inline_container_width_incl: bool | None = None
        self._max_inline_list_or_dict_width_excl: bool | None = None

        if constraints.max_inline_container_width_incl is not None:
            self._max_inline_container_width_incl = (
                max_inline_container_width_incl is not None
                and max_inline_container_width_incl <= constraints.max_inline_container_width_incl)

        if constraints.max_inline_list_or_dict_width_excl is not None:
            self._max_inline_list_or_dict_width_excl = (
                max_inline_list_or_dict_width_excl is not None
                and max_inline_list_or_dict_width_excl
                <= constraints.max_inline_list_or_dict_width_excl)

    @property
    def max_inline_container_width_incl(self) -> bool | None:
        return self._max_inline_container_width_incl

    @property
    def max_inline_list_or_dict_width_excl(self) -> bool | None:
        return self._max_inline_list_or_dict_width_excl

    def __repr__(self) -> str:
        return (f'ConstraintsSatisfaction('
                f'max_inline_container_width_incl={self.max_inline_container_width_incl}, '
                f'max_inline_list_or_dict_width_excl={self.max_inline_list_or_dict_width_excl}'
                f')')
