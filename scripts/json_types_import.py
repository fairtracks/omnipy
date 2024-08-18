from pathlib import Path
import sys

project_dir = Path(__file__).parent.parent.parent.parent.parent
omnipy_json_dir = project_dir / 'src' / 'omnipy' / 'modules' / 'json'
prev_sys_path = sys.path
sys.path = [omnipy_json_dir.as_posix()]

from typedefs import Json  # noqa
from typedefs import JsonDict  # noqa
from typedefs import JsonDictOfDicts  # noqa
from typedefs import JsonDictOfDictsOfScalars  # noqa
from typedefs import JsonDictOfLists  # noqa
from typedefs import JsonDictOfListsOfDicts  # noqa
from typedefs import JsonDictOfListsOfScalars  # noqa
from typedefs import JsonDictOfNestedLists  # noqa
from typedefs import JsonDictOfScalars  # noqa
from typedefs import JsonList  # noqa
from typedefs import JsonListOfDicts  # noqa
from typedefs import JsonListOfDictsOfScalars  # noqa
from typedefs import JsonListOfLists  # noqa
from typedefs import JsonListOfListsOfScalars  # noqa
from typedefs import JsonListOfNestedDicts  # noqa
from typedefs import JsonListOfScalars  # noqa
from typedefs import JsonNestedDicts  # noqa
from typedefs import JsonNestedLists  # noqa
from typedefs import JsonOnlyDicts  # noqa
from typedefs import JsonOnlyLists  # noqa
from typedefs import JsonScalar  # noqa

sys.path = prev_sys_path
