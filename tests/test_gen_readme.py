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


def test_formatted_error_is_separate_from_copyable_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / 'source.md'
    source.write_text(
        '```pycon\n'
        '>>> value = 1\n'
        '>>> value / 0\n'
        '```\n\n'
        '```pycon exec="1"\n'
        '>>> print(\'!!! error "ZeroDivisionError"\\n\\n    ```\\n'
        "    division by zero\\n    ```')\n"
        '```\n'
    )
    target = tmp_path / 'README.md'
    monkeypatch.setattr(gen_readme, 'SOURCE', source)
    monkeypatch.setattr(om, 'runtime', MagicMock())

    gen_readme.ReadmeGenerator().generate(target, tmp_path / 'images')

    assert (
        '```pycon\n>>> value = 1\n>>> value / 0\n```\n\n'
        '```text\nZeroDivisionError: division by zero\n```'
    ) in target.read_text()


@pytest.mark.parametrize(
    ('readme', 'image_name', 'expected'),
    [
        ('generated readme', 'image.svg', True),
        ('old readme', 'image.svg', False),
        ('generated readme', 'old.svg', False),
    ],
)
def test_check_compares_readme_and_image_names(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    readme: str,
    image_name: str,
    expected: bool,
) -> None:
    target = tmp_path / 'README.md'
    target.write_text(readme)
    images = tmp_path / 'images'
    images.mkdir()
    (images / image_name).write_text('different image content')

    def generate(self: gen_readme.ReadmeGenerator, target: Path, image_dir: Path) -> None:
        target.write_text('generated readme')
        image_dir.mkdir()
        (image_dir / 'image.svg').write_text('generated image content')

    monkeypatch.setattr(gen_readme.ReadmeGenerator, 'generate', generate)
    assert gen_readme.check_generated_readme(target, images) is expected
    assert (images / image_name).read_text() == 'different image content'
