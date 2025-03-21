import omnipy.util._pydantic as pyd


@pyd.dataclass(
    kw_only=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True))
class Constraints:
    """Constraints for display of content."""

    container_width_per_line_limit: pyd.NonNegativeInt | None = None
    """
    Limit of character width for any Python container (e.g. list, tuple, dict, object) per line.
    Used internally in DevtoolsPrettyPrinter to manage the `simple_cutoff` parameter.
    """


class ConstraintsSatisfaction:
    def __init__(self,
                 constraints: Constraints,
                 *,
                 max_container_width_across_lines: int | None = None) -> None:
        self._container_width_per_line_limit: bool | None = None

        if constraints.container_width_per_line_limit is not None:
            self._container_width_per_line_limit = (
                max_container_width_across_lines is not None
                and max_container_width_across_lines <= constraints.container_width_per_line_limit)

    @property
    def container_width_per_line_limit(self) -> bool | None:
        return self._container_width_per_line_limit
