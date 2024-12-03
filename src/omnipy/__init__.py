__version__ = '0.17.2'

import os

from omnipy.compute.flow import (DagFlow,
                                 DagFlowTemplate,
                                 FuncFlow,
                                 FuncFlowTemplate,
                                 LinearFlow,
                                 LinearFlowTemplate)
from omnipy.compute.task import Task, TaskTemplate
from omnipy.data.dataset import Dataset, MultiModelDataset
from omnipy.data.model import Model
from omnipy.data.param import (bind_adjust_dataset_func,
                               bind_adjust_model_func,
                               params_dataclass,
                               ParamsBase)
from omnipy.hub.runtime import runtime
from omnipy.modules.general.models import (Chain2,
                                           Chain3,
                                           Chain4,
                                           Chain5,
                                           Chain6,
                                           NotIterableExceptStrOrBytesModel)
from omnipy.modules.general.tasks import convert_dataset, import_directory, split_dataset
from omnipy.modules.isa import (flatten_isa_json,
                                FlattenedIsaJsonDataset,
                                FlattenedIsaJsonModel,
                                IsaJsonDataset,
                                IsaJsonModel)
from omnipy.modules.isa.models import IsaInvestigationModel, IsaTopLevelModel
from omnipy.modules.isa.models.assay_schema import IsaAssayJsonModel
from omnipy.modules.isa.models.comment_schema import IsaCommentModel
from omnipy.modules.isa.models.data_schema import IsaDataModel
from omnipy.modules.isa.models.factor_schema import IsaFactorModel
from omnipy.modules.isa.models.factor_value_schema import IsaFactorValueModel
from omnipy.modules.isa.models.material_attribute_schema import IsaMaterialAttributeModel
from omnipy.modules.isa.models.material_attribute_value_schema import IsaMaterialAttributeValueModel
from omnipy.modules.isa.models.material_schema import IsaMaterialModel
from omnipy.modules.isa.models.ontology_annotation_schema import IsaOntologyReferenceModel
from omnipy.modules.isa.models.ontology_source_reference_schema import \
    IsaOntologySourceReferenceModel
from omnipy.modules.isa.models.organization_schema import IsaOrganizationModel
from omnipy.modules.isa.models.person_schema import IsaPersonModel
from omnipy.modules.isa.models.process_parameter_value_schema import IsaProcessParameterValueModel
from omnipy.modules.isa.models.process_schema import IsaProcessOrProtocolApplicationModel
from omnipy.modules.isa.models.protocol_parameter_schema import IsaProtocolParameterModel
from omnipy.modules.isa.models.protocol_schema import IsaProtocolModel
from omnipy.modules.isa.models.publication_schema import IsaPublicationModel
from omnipy.modules.isa.models.sample_schema import IsaSampleModel
from omnipy.modules.isa.models.source_schema import IsaSourceModel
from omnipy.modules.isa.models.study_group import IsaStudyGroupModel
from omnipy.modules.isa.models.study_schema import IsaStudyModel
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
from omnipy.modules.json.flows import (flatten_nested_json,
                                       transpose_dict_of_dicts_2_list_of_dicts,
                                       transpose_dicts_of_lists_of_dicts_2_lists_of_dicts)
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
from omnipy.modules.json.tasks import convert_dataset_string_to_json, transpose_dicts_2_lists
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
                                       MatchItemsModel,
                                       NestedJoinItemsModel,
                                       NestedSplitToItemsModel,
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
from omnipy.modules.remote.datasets import HttpUrlDataset
from omnipy.modules.remote.models import HttpUrlModel, QueryParamsModel, UrlPathModel
from omnipy.modules.remote.tasks import (async_load_urls_into_new_dataset,
                                         get_bytes_from_api_endpoint,
                                         get_json_from_api_endpoint,
                                         get_str_from_api_endpoint,
                                         load_urls_into_new_dataset)
from omnipy.modules.tables.datasets import (CsvTableDataset,
                                            TableDictOfDictsOfJsonScalarsDataset,
                                            TableDictOfListsOfJsonScalarsDataset,
                                            TableListOfDictsOfJsonScalarsDataset,
                                            TableListOfListsOfJsonScalarsDataset,
                                            TableOfPydanticRecordsDataset,
                                            TableWithColNamesDataset,
                                            TsvTableDataset)
from omnipy.modules.tables.models import (CsvTableModel,
                                          PydanticRecordModel,
                                          TableDictOfDictsOfJsonScalarsModel,
                                          TableDictOfListsOfJsonScalarsModel,
                                          TableListOfDictsOfJsonScalarsModel,
                                          TableListOfListsOfJsonScalarsModel,
                                          TableOfPydanticRecordsModel,
                                          TableWithColNamesModel,
                                          TsvTableModel)
from omnipy.modules.tables.tasks import (create_row_index_from_column,
                                         remove_columns,
                                         rename_col_names,
                                         transpose_columns_with_data_files)
from omnipy.util.contexts import print_exception

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
    'MultiModelDataset',
    'Model',
    'FlattenedIsaJsonDataset',
    'FlattenedIsaJsonModel',
    'IsaJsonModel',
    'IsaJsonDataset',
    'IsaInvestigationModel',
    'IsaTopLevelModel',
    'IsaAssayJsonModel',
    'IsaCommentModel',
    'IsaDataModel',
    'IsaFactorModel',
    'IsaFactorValueModel',
    'IsaMaterialAttributeModel',
    'IsaMaterialAttributeValueModel',
    'IsaMaterialModel',
    'IsaOntologyReferenceModel',
    'IsaOntologySourceReferenceModel',
    'IsaOrganizationModel',
    'IsaPersonModel',
    'IsaProcessParameterValueModel',
    'IsaProcessOrProtocolApplicationModel',
    'IsaProtocolParameterModel',
    'IsaProtocolModel',
    'IsaPublicationModel',
    'IsaSampleModel',
    'IsaSourceModel',
    'IsaStudyGroupModel',
    'IsaStudyModel',
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
    'NestedJoinItemsModel',
    'NestedSplitToItemsModel',
    'MatchItemsModel',
    'StrModel',
    'CsvTableDataset',
    'TableDictOfDictsOfJsonScalarsDataset',
    'TableDictOfListsOfJsonScalarsDataset',
    'TableListOfListsOfJsonScalarsDataset',
    'TableListOfDictsOfJsonScalarsDataset',
    'TableOfPydanticRecordsDataset',
    'TableWithColNamesDataset',
    'TsvTableDataset',
    'CsvTableModel',
    'PydanticRecordModel',
    'TableOfPydanticRecordsModel',
    'TableWithColNamesModel',
    'TableDictOfDictsOfJsonScalarsModel',
    'TableDictOfListsOfJsonScalarsModel',
    'TableListOfDictsOfJsonScalarsModel',
    'TableListOfListsOfJsonScalarsModel',
    'TsvTableModel',
    'bind_adjust_model_func',
    'bind_adjust_dataset_func',
    'params_dataclass',
    'ParamsBase',
    'NotIterableExceptStrOrBytesModel',
    'Chain2',
    'Chain3',
    'Chain4',
    'Chain5',
    'Chain6',
    'import_directory',
    'split_dataset',
    'convert_dataset',
    'flatten_isa_json',
    'flatten_nested_json',
    'convert_dataset_string_to_json',
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
    'QueryParamsModel',
    'HttpUrlModel',
    'UrlPathModel',
    'HttpUrlDataset',
    'get_bytes_from_api_endpoint',
    'get_json_from_api_endpoint',
    'get_str_from_api_endpoint',
    'async_load_urls_into_new_dataset',
    'load_urls_into_new_dataset',
    'create_row_index_from_column',
    'remove_columns',
    'rename_col_names',
    'transpose_columns_with_data_files',
    'print_exception',
]
