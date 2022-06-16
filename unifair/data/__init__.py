from data.json import JsonDatasetToTarFileSerializer
from data.pandas import PandasDatasetToTarFileSerializer

DEFAULT_RESULT_TYPE_TO_SERIALIZER_MAP = {
    'JsonDataset': JsonDatasetToTarFileSerializer,
    'PandasDataset': PandasDatasetToTarFileSerializer
}
