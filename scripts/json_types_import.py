from pathlib import Path
import sys

project_dir = Path(__file__).parent.parent.parent.parent.parent
omnipy_json_dir = project_dir / 'src' / 'omnipy' / 'components' / 'json'
prev_sys_path = sys.path
sys.path = [omnipy_json_dir.as_posix()]

from typedefs import (  # noqa: E402
    Json,
    JsonDict,
    JsonDictOfDicts,
    JsonDictOfDictsOfScalars,
    JsonDictOfLists,
    JsonDictOfListsOfDicts,
    JsonDictOfListsOfScalars,
    JsonDictOfNestedLists,
    JsonDictOfScalars,
    JsonList,
    JsonListOfDicts,
    JsonListOfDictsOfScalars,
    JsonListOfLists,
    JsonListOfListsOfScalars,
    JsonListOfNestedDicts,
    JsonListOfScalars,
    JsonNestedDicts,
    JsonNestedLists,
    JsonOnlyDicts,
    JsonOnlyLists,
    JsonScalar,
)

__all__ = [
    'Json',
    'JsonDict',
    'JsonDictOfDicts',
    'JsonDictOfDictsOfScalars',
    'JsonDictOfLists',
    'JsonDictOfListsOfDicts',
    'JsonDictOfListsOfScalars',
    'JsonDictOfNestedLists',
    'JsonDictOfScalars',
    'JsonList',
    'JsonListOfDicts',
    'JsonListOfDictsOfScalars',
    'JsonListOfLists',
    'JsonListOfListsOfScalars',
    'JsonListOfNestedDicts',
    'JsonListOfScalars',
    'JsonNestedDicts',
    'JsonNestedLists',
    'JsonOnlyDicts',
    'JsonOnlyLists',
    'JsonScalar',
]

sys.path = prev_sys_path
