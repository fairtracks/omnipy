from dataclasses import dataclass, field
from typing import Optional

from omnipy.api.protocols import IsRuntime
from omnipy.hub.publisher import ConfigPublisher


@dataclass
class RuntimeEntryPublisher(ConfigPublisher):
    _back: Optional[IsRuntime] = field(default=None, init=False, repr=False)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if hasattr(self, key) and not key.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()
