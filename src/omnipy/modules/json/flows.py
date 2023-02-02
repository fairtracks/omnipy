from omnipy.compute.flow import FuncFlowTemplate
from omnipy.modules.json.datasets import (JsonListOfDictsOfAnyDataset,
                                          JsonListOfDictsOfScalarsDataset)
from omnipy.modules.json.tasks import (DEFAULT_KEY,
                                       flatten_outer_level_of_all_data_files,
                                       ID_KEY,
                                       REF_KEY)


@FuncFlowTemplate(fixed_params=dict(id_key=ID_KEY, ref_key=REF_KEY, default_key=DEFAULT_KEY))
def flatten_nested_json(
    dataset: JsonListOfDictsOfAnyDataset,
    id_key: str,
    ref_key: str,
    default_key: str,
) -> JsonListOfDictsOfScalarsDataset:
    all_data_files_of_scalar_records_ds = JsonListOfDictsOfScalarsDataset()
    data_files_of_any_ds = dataset

    while len(data_files_of_any_ds) > 0:
        data_files_of_scalar_records_ds, data_files_of_any_ds = \
            flatten_outer_level_of_all_data_files(
                data_files_of_any_ds, id_key, ref_key, default_key)

        all_data_files_of_scalar_records_ds |= data_files_of_scalar_records_ds

    return all_data_files_of_scalar_records_ds
