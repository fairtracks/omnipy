from dataclasses import dataclass, field
from typing import Optional

from omnipy.api.protocols import IsRuntime
from omnipy.util.publisher import DataPublisher


@dataclass
class RuntimeEntryPublisher(DataPublisher):
    _back: Optional[IsRuntime] = field(default=None, init=False, repr=False)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if hasattr(self, key) and not key.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()
