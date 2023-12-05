from typing import ClassVar, Dict, Protocol


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict]
