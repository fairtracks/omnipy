"""State of the local paged observation service."""

from dataclasses import dataclass, field


@dataclass
class PagedObservationService:
    base_url: str = ''
    records: list[dict[str, object]] = field(default_factory=list)
    requests: list[tuple[int, int]] = field(default_factory=list)
    responses: dict[int, object] = field(default_factory=dict)
