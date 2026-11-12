from pathlib import Path
from unittest.mock import MagicMock

from docs import gen_readme
import pytest

import omnipy as om


def test_generation_failure_preserves_existing_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / 'source.md'
    source.write_text('```unsupported exec="1"\n```\n')
    target = tmp_path / 'README.md'
    target.write_text('existing readme')
    images = tmp_path / 'images'
    images.mkdir()
    image = images / 'existing.svg'
    image.write_text('existing image')
    monkeypatch.setattr(gen_readme, 'SOURCE', source)
    monkeypatch.setattr(gen_readme, 'TARGET', target)
    monkeypatch.setattr(gen_readme, 'IMAGE_DIR', images)
    monkeypatch.setattr(om, 'runtime', MagicMock())

    with pytest.raises(ValueError, match='Unsupported executable fence'):
        gen_readme.ReadmeGenerator().generate()

    assert target.read_text() == 'existing readme'
    assert image.read_text() == 'existing image'
