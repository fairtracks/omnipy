from unifair import runtime
from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.modules.general.tasks import import_directory
from unifair.modules.json.models import JsonDataset, JsonDict, JsonType
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.raw.tasks import modify_datafile_contents
from unifair.modules.raw.util import serialize_to_tarpacked_raw_files

runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False

# from unifair.modules.r_stat import r

# Regex patterns for parsing
#     variable_pattern = re.compile(r"  type discrete \[ \d+ \] \{ (.+) \};\s*")
#     prior_probability_pattern_1 = re.compile(
#         r"probability \( ([^|]+) \) \{\s*")
#     prior_probability_pattern_2 = re.compile(r"  table (.+);\s*")
#     conditional_probability_pattern_1 = (
#         re.compile(r"probability \( (.+) \| (.+) \) \{\s*"))
#     conditional_probability_pattern_2 = re.compile(r"  \((.+)\) (.+);\s*")

# @TaskTemplate
# def import_dag_from_bnlearn(dag_name: str):
#     r('chooseCRANmirror(ind = 1)')
#     r('install.binaries("bnlearn")')
#     r('library(bnlearn)')
#     # r('install.packages("https://www.bnlearn.com/releases/bnlearn_latest.tar.gz", '
#     #   'repos = NULL, type = "source")')


def convert_to_json(contents: str, **kwargs: object):
    contents = contents.replace('\n', '')
    return f'"{contents}"'


data_raw = import_directory.run('input/bif', suffix='.bif')
data_raw_2 = modify_datafile_contents.run(data_raw, convert_to_json)


@TaskTemplate
def convert(
        dataset: Dataset[Model[JsonDict[JsonType]]]
) -> Dataset[Model[JsonDict[JsonDict[JsonType]]]]:
    pass


serialize_to_tarpacked_raw_files('1_data_raw', data_raw)
serialize_to_tarpacked_raw_files('2_data_raw', data_raw_2)
