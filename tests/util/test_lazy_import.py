from pathlib import Path
import sys

import pytest

from omnipy.util.lazy_import import resolve_lazy_export


def test_resolve_lazy_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    package = tmp_path / 'lazy_export_test_package'
    package.mkdir()
    (package / '__init__.py').write_text('')
    (package / 'first.py').write_text('first = object()\n')
    (package / 'second.py').write_text('second = object()\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    namespace: dict[str, object] = {}
    exports = {'first': '.first', 'second': 'lazy_export_test_package.second'}

    assert 'lazy_export_test_package.first' not in sys.modules
    module_name = 'lazy_export_test_package.facade'
    package_name = 'lazy_export_test_package'
    first = resolve_lazy_export('first', module_name, package_name, namespace, exports)
    assert namespace['first'] is first
    assert 'lazy_export_test_package.first' in sys.modules
    assert 'lazy_export_test_package.second' not in sys.modules

    second = resolve_lazy_export('second', module_name, package_name, namespace, exports)
    assert namespace['second'] is second
    with pytest.raises(
        AttributeError, match="module 'lazy_export_test_package.facade' has no attribute"
    ):
        resolve_lazy_export('missing', module_name, package_name, namespace, exports)
