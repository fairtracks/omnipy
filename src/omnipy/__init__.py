__version__ = '0.15.6'

import os

from omnipy.compute.flow import (DagFlow,
                                 DagFlowTemplate,
                                 FuncFlow,
                                 FuncFlowTemplate,
                                 LinearFlow,
                                 LinearFlowTemplate)
from omnipy.compute.task import Task, TaskTemplate
from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset
from omnipy.data.model import ListOfParamModel, Model, ParamModel
from omnipy.hub.runtime import runtime
# from omnipy.util.helpers import recursive_module_import
from omnipy.modules.general.tasks import convert_dataset, import_directory, split_dataset
from omnipy.modules.isa import (flatten_isa_json,
                                FlattenedIsaJsonDataset,
                                FlattenedIsaJsonModel,
                                IsaJsonDataset,
                                IsaJsonModel)
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
from omnipy.modules.json.models import (JsonCustomDictModel,
                                        JsonCustomListModel,
                                        JsonDictModel,
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
from omnipy.modules.pandas.tasks import (cartesian_product,
                                         concat_dataframes_across_datasets,
                                         convert_dataset_csv_to_pandas,
                                         convert_dataset_list_of_dicts_to_pandas,
                                         convert_dataset_pandas_to_csv,
                                         extract_columns_as_files,
                                         join_tables)
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
from omnipy.modules.tables.datasets import TableOfPydanticRecordsDataset, TableWithColNamesDataset
from omnipy.modules.tables.models import TableOfPydanticRecordsModel, TableWithColNamesModel
from omnipy.modules.tables.tasks import (remove_columns,
                                         rename_col_names,
                                         transpose_columns_with_data_files)

# from omnipy.util.helpers import recursive_module_import

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

__all__ = [
    'runtime',
    'DagFlow',
    'DagFlowTemplate',
    'FuncFlow',
    'FuncFlowTemplate',
    'LinearFlow',
    'LinearFlowTemplate',
    'Task',
    'TaskTemplate',
    'Dataset',
    'ParamDataset',
    'ListOfParamModelDataset',
    'Model',
    'ParamModel',
    'ListOfParamModel',
    'FlattenedIsaJsonDataset',
    'FlattenedIsaJsonModel',
    'IsaJsonModel',
    'IsaJsonDataset',
    'JsonCustomDictModel',
    'JsonCustomListModel',
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
    'TableOfPydanticRecordsDataset',
    'TableWithColNamesDataset',
    'TableOfPydanticRecordsModel',
    'TableWithColNamesModel',
    'import_directory',
    'split_dataset',
    'convert_dataset',
    'flatten_isa_json',
    'flatten_nested_json',
    'transpose_dicts_2_lists',
    'transpose_dict_of_dicts_2_list_of_dicts',
    'transpose_dicts_of_lists_of_dicts_2_lists_of_dicts',
    'concat_dataframes_across_datasets',
    'convert_dataset_csv_to_pandas',
    'convert_dataset_pandas_to_csv',
    'convert_dataset_list_of_dicts_to_pandas',
    'extract_columns_as_files',
    'join_tables',
    'cartesian_product',
    'decode_bytes',
    'modify_all_lines',
    'modify_datafile_contents',
    'modify_each_line',
    'concat_all',
    'union_all',
    'remove_columns',
    'rename_col_names',
    'transpose_columns_with_data_files'
]

#
# def __getattr__(attr_name: str) -> object:
#     omnipy = importlib.import_module(__name__)
#     all_modules = []
#     recursive_module_import(omnipy, all_modules)
#     print(all_modules)
