from datetime import datetime
import os

from omnipy import ROOT_DIR
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .serializers import RawDatasetToTarFileSerializer


def serialize_to_tarpacked_raw_files(dataset_name: str, dataset: Dataset[Model[str]]) -> None:
    """
    Serializing is not fully implemented, so here is a helper method to write a dataset to a
    dataset_name.tar.gz file with a set of csv files, one for each data item (endpoint/table)
    """
    data_dir = os.path.join(ROOT_DIR,
                            '..',
                            '..',
                            'data',
                            datetime.now().strftime('%Y_%m_%d-%H_%M_%S'))

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_path = os.path.join(data_dir, dataset_name + '.tar.gz')

    print('Writing dataset as a gzipped tarpack of raw files to "{}"'.format(
        os.path.abspath(file_path)))
    serializer = RawDatasetToTarFileSerializer()
    with open(file_path, 'wb') as tarfile:
        tarfile.write(serializer.serialize(dataset))
