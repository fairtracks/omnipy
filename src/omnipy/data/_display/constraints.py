from omnipy.util._pydantic import ConfigDict, dataclass, Extra, NonNegativeInt


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid, validate_assignment=True))
class Constraints:
    container_width_per_line_limit: NonNegativeInt | None = None


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
