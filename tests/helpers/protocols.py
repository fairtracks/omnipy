from typing import Protocol

from omnipy.shared.typedefs import TypeForm


class AssertModelOrValFunc(Protocol):
    def __call__(
        self,
        model_or_val: object,
        target_type: TypeForm,
        content: object,
    ) -> None:
        ...
