from datetime import datetime
import os

from omnipy import ROOT_DIR
from omnipy.data.dataset import Dataset

from .models import PandasDataset
from .serializers import PandasDatasetToTarFileSerializer


def serialize_to_tarpacked_csv_files(dataset_name: str, dataset: Dataset) -> None:
    """
    Serializing is not fully implemented, so here is a helper method to write a dataset to a
    dataset_name.tar.gz file with a set of csv files, one for each data item (endpoint/table)
    """
    pandas_dataset = PandasDataset()
    pandas_dataset.from_data(dataset.to_data())

    data_dir = os.path.join(ROOT_DIR,
                            '..',
                            '..',
                            'data',
                            datetime.now().strftime('%Y_%m_%d-%H_%M_%S'))

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_path = os.path.join(data_dir, dataset_name + '.tar.gz')

    print('Writing dataset as a gzipped tarpack of CSV files to "{}"'.format(
        os.path.abspath(file_path)))
    serializer = PandasDatasetToTarFileSerializer()
    with open(file_path, 'wb') as tarfile:
        tarfile.write(serializer.serialize(pandas_dataset))
