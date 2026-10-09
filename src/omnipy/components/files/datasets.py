from typing import TYPE_CHECKING

from omnipy.data.dataset import Dataset

if TYPE_CHECKING:
    from ..raw.models import StrictBytesModel, StrModel  # noqa: F401


class GeneralFileDataset(Dataset['GeneralFileDataset | StrModel | StrictBytesModel']):
    ...
