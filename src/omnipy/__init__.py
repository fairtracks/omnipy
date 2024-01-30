__version__ = '0.14.10'

import os

from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset
from omnipy.data.model import ListOfParamModel, Model, ParamModel
from omnipy.hub.runtime import runtime
# from omnipy.util.helpers import recursive_module_import
from omnipy.modules.general.tasks import import_directory, split_dataset
from omnipy.modules.json.datasets import (JsonDataset,
                                          JsonDictDataset,
                                          JsonDictOfDictsDataset,
                                          JsonDictOfDictsOfScalarsDataset,
                                          JsonDictOfListsDataset,
                                          JsonDictOfListsOfDictsDataset,
                                          JsonDictOfListsOfScalarsDataset,
                                          JsonDictOfNestedListsDataset,
                                          JsonDictOfScalarsDataset,
                                          JsonListDataset,
                                          JsonListOfDictsDataset,
                                          JsonListOfDictsOfScalarsDataset,
                                          JsonListOfListsDataset,
                                          JsonListOfListsOfScalarsDataset,
                                          JsonListOfNestedDictsDataset,
                                          JsonListOfScalarsDataset,
                                          JsonNestedDictsDataset,
                                          JsonNestedListsDataset,
                                          JsonOnlyDictsDataset,
                                          JsonOnlyListsDataset,
                                          JsonScalarDataset)
from omnipy.modules.json.flows import flatten_nested_json
from omnipy.modules.json.models import (JsonDictModel,
                                        JsonDictOfDictsModel,
                                        JsonDictOfDictsOfScalarsModel,
                                        JsonDictOfListsModel,
                                        JsonDictOfListsOfDictsModel,
                                        JsonDictOfListsOfScalarsModel,
                                        JsonDictOfNestedListsModel,
                                        JsonDictOfScalarsModel,
                                        JsonListModel,
                                        JsonListOfDictsModel,
                                        JsonListOfDictsOfScalarsModel,
                                        JsonListOfListsModel,
                                        JsonListOfListsOfScalarsModel,
                                        JsonListOfNestedDictsModel,
                                        JsonListOfScalarsModel,
                                        JsonModel,
                                        JsonNestedDictsModel,
                                        JsonNestedListsModel,
                                        JsonOnlyDictsModel,
                                        JsonOnlyListsModel,
                                        JsonScalarModel)
from omnipy.modules.json.tasks import (transpose_dict_of_dicts_2_list_of_dicts,
                                       transpose_dicts_2_lists,
                                       transpose_dicts_of_lists_of_dicts_2_lists_of_dicts)
from omnipy.modules.pandas.models import (ListOfPandasDatasetsWithSameNumberOfFiles,
                                          PandasDataset,
                                          PandasModel)
from omnipy.modules.pandas.tasks import (concat_dataframes_across_datasets,
                                         convert_dataset_csv_to_pandas,
                                         convert_dataset_list_of_dicts_to_pandas,
                                         convert_dataset_pandas_to_csv,
                                         extract_columns_as_files)
from omnipy.modules.raw.datasets import (BytesDataset,
                                         JoinColumnsToLinesDataset,
                                         JoinItemsDataset,
                                         JoinLinesDataset,
                                         SplitLinesToColumnsDataset,
                                         SplitToItemsDataset,
                                         SplitToLinesDataset,
                                         StrDataset)
from omnipy.modules.raw.models import (BytesModel,
                                       JoinColumnsToLinesModel,
                                       JoinItemsModel,
                                       JoinLinesModel,
                                       SplitLinesToColumnsModel,
                                       SplitToItemsModel,
                                       SplitToLinesModel,
                                       StrModel)
from omnipy.modules.raw.tasks import (concat_all,
                                      decode_bytes,
                                      modify_all_lines,
                                      modify_datafile_contents,
                                      modify_each_line,
                                      union_all)
from omnipy.modules.tables.tasks import remove_columns

# from omnipy.util.helpers import recursive_module_import

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

__all__ = [
    'runtime',
    'Dataset',
    'ParamDataset',
    'ListOfParamModelDataset',
    'Model',
    'ParamModel',
    'ListOfParamModel',
    'JsonDataset',
    'JsonDictDataset',
    'JsonDictOfDictsDataset',
    'JsonDictOfDictsOfScalarsDataset',
    'JsonDictOfListsDataset',
    'JsonDictOfListsOfDictsDataset',
    'JsonDictOfListsOfScalarsDataset',
    'JsonDictOfNestedListsDataset',
    'JsonDictOfScalarsDataset',
    'JsonListDataset',
    'JsonListOfDictsDataset',
    'JsonListOfDictsOfScalarsDataset',
    'JsonListOfListsDataset',
    'JsonListOfListsOfScalarsDataset',
    'JsonListOfNestedDictsDataset',
    'JsonListOfScalarsDataset',
    'JsonNestedDictsDataset',
    'JsonNestedListsDataset',
    'JsonOnlyDictsDataset',
    'JsonOnlyListsDataset',
    'JsonScalarDataset',
    'JsonDictModel',
    'JsonDictOfDictsModel',
    'JsonDictOfDictsOfScalarsModel',
    'JsonDictOfListsModel',
    'JsonDictOfListsOfDictsModel',
    'JsonDictOfListsOfScalarsModel',
    'JsonDictOfNestedListsModel',
    'JsonDictOfScalarsModel',
    'JsonListModel',
    'JsonListOfDictsModel',
    'JsonListOfDictsOfScalarsModel',
    'JsonListOfListsModel',
    'JsonListOfListsOfScalarsModel',
    'JsonListOfNestedDictsModel',
    'JsonListOfScalarsModel',
    'JsonModel',
    'JsonNestedDictsModel',
    'JsonNestedListsModel',
    'JsonOnlyDictsModel',
    'JsonOnlyListsModel',
    'JsonScalarModel',
    'ListOfPandasDatasetsWithSameNumberOfFiles',
    'PandasModel',
    'PandasDataset',
    'BytesDataset',
    'SplitToLinesDataset',
    'JoinLinesDataset',
    'SplitToItemsDataset',
    'JoinItemsDataset',
    'SplitLinesToColumnsDataset',
    'JoinColumnsToLinesDataset',
    'StrDataset',
    'BytesModel',
    'SplitToLinesModel',
    'JoinLinesModel',
    'SplitToItemsModel',
    'JoinItemsModel',
    'SplitLinesToColumnsModel',
    'JoinColumnsToLinesModel',
    'StrModel',
    'import_directory',
    'split_dataset',
    'flatten_nested_json',
    'transpose_dicts_2_lists',
    'transpose_dict_of_dicts_2_list_of_dicts',
    'transpose_dicts_of_lists_of_dicts_2_lists_of_dicts',
    'concat_dataframes_across_datasets',
    'convert_dataset_csv_to_pandas',
    'convert_dataset_pandas_to_csv',
    'convert_dataset_list_of_dicts_to_pandas',
    'extract_columns_as_files',
    'decode_bytes',
    'modify_all_lines',
    'modify_datafile_contents',
    'modify_each_line',
    'concat_all',
    'union_all',
    'remove_columns',
]

#
# def __getattr__(attr_name: str) -> object:
#     omnipy = importlib.import_module(__name__)
#     all_modules = []
#     recursive_module_import(omnipy, all_modules)
#     print(all_modules)
