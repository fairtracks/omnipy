from io import BytesIO
from zipfile import ZipFile

from omnipy.data.model import Model

from ..raw.models import StrictBytesModel, StrModel  # noqa: F401
from .datasets import GeneralFileDataset


class ZipFileModel(Model[GeneralFileDataset | StrictBytesModel]):
    @classmethod
    def _parse_data(
            cls,
            data: GeneralFileDataset | StrictBytesModel) -> GeneralFileDataset | StrictBytesModel:

        if isinstance(data, StrictBytesModel):
            from .datasets import GeneralFileDataset

            root = GeneralFileDataset()
            with ZipFile(BytesIO(data.content)) as zip_file:
                for info in zip_file.infolist():
                    if info.is_dir():
                        continue
                    *dir_names, file_name = [part for part in info.filename.split('/') if part]
                    node = root
                    for dir_name in dir_names:
                        if dir_name not in node:
                            node[dir_name] = GeneralFileDataset()
                        node = node[dir_name]
                    node[file_name] = zip_file.read(info)
            return root
        return data


GeneralFileDataset.update_forward_refs()
ZipFileModel.update_forward_refs()
