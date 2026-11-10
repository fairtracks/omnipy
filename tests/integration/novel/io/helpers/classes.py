"""State of the local services for loading and posting."""

from dataclasses import dataclass, field


@dataclass
class PagedObservationService:
    base_url: str = ''
    records: list[dict[str, object]] = field(default_factory=list)
    requests: list[tuple[int, int]] = field(default_factory=list)
    responses: dict[int, object] = field(default_factory=dict)


@dataclass
class PostService:
    """Local service doubling posted values, recording the request bodies it receives."""

    base_url: str = ''
    requests: list[object] = field(default_factory=list)
    # Status code of the first response from the "/fails-once" endpoint
    first_status: int = 503

    def url(self, endpoint: str) -> str:
        return f'{self.base_url}{endpoint}'
