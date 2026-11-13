"""Tests for the skills shipped with Omnipy and their installation."""

from pathlib import Path
import re

import pytest

from omnipy.skills import install, SKILL_FILE, skill_names, skill_path, skills_dir
from omnipy.skills.cli import main

DATAFLOWS_SKILL = 'omnipy-dataflows'
FRONTMATTER_NAME_RE = re.compile(r'^---\nname: (?P<name>\S+)\n', re.M)


def test_shipped_skills() -> None:
    assert DATAFLOWS_SKILL in skill_names()
    for name in skill_names():
        path = skill_path(name)
        assert path.parent == skills_dir()
        match = FRONTMATTER_NAME_RE.match((path / SKILL_FILE).read_text())
        assert match and match['name'] == name


def test_unknown_skill() -> None:
    with pytest.raises(LookupError, match=DATAFLOWS_SKILL):
        skill_path('no-such-skill')


def test_install_links_by_default(tmp_path: Path) -> None:
    installed = install(DATAFLOWS_SKILL, tmp_path / 'skills')

    assert installed.linked
    assert installed.path == tmp_path / 'skills' / DATAFLOWS_SKILL
    assert installed.path.is_symlink()
    assert installed.path.resolve() == skill_path(DATAFLOWS_SKILL).resolve()


def test_install_copy(tmp_path: Path) -> None:
    installed = install(DATAFLOWS_SKILL, tmp_path, copy=True)

    assert not installed.linked
    assert not installed.path.is_symlink()
    source = skill_path(DATAFLOWS_SKILL)
    copied_files = sorted(p.relative_to(installed.path) for p in installed.path.rglob('*'))
    assert copied_files == sorted(p.relative_to(source) for p in source.rglob('*'))
    assert (installed.path / SKILL_FILE).read_text() == (source / SKILL_FILE).read_text()


def test_install_existing(tmp_path: Path) -> None:
    install(DATAFLOWS_SKILL, tmp_path, copy=True)
    with pytest.raises(FileExistsError, match='exists'):
        install(DATAFLOWS_SKILL, tmp_path)

    replaced = install(DATAFLOWS_SKILL, tmp_path, force=True)
    assert replaced.linked and replaced.path.is_symlink()

    replaced_again = install(DATAFLOWS_SKILL, tmp_path, copy=True, force=True)
    assert not replaced_again.linked and not replaced_again.path.is_symlink()


def test_cli_list_and_path(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(['list']) == 0
    assert capsys.readouterr().out.splitlines() == skill_names()

    assert main(['path', DATAFLOWS_SKILL]) == 0
    assert capsys.readouterr().out.strip() == str(skill_path(DATAFLOWS_SKILL))


def test_cli_install_into_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(['install', DATAFLOWS_SKILL]) == 0
    linked = tmp_path / '.agents' / 'skills' / DATAFLOWS_SKILL
    assert linked.is_symlink()
    assert capsys.readouterr().out.startswith(f'linked {DATAFLOWS_SKILL} -> ')

    assert main(['install', '--claude', '--mode', 'copy', DATAFLOWS_SKILL]) == 0
    copied = tmp_path / '.claude' / 'skills' / DATAFLOWS_SKILL
    assert (copied / SKILL_FILE).is_file() and not copied.is_symlink()

    assert main(['install', DATAFLOWS_SKILL]) == 1
    assert 'exists' in capsys.readouterr().err
    assert main(['install', '--force', DATAFLOWS_SKILL]) == 0


def test_cli_install_into_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: tmp_path))

    assert main(['install', '--home', DATAFLOWS_SKILL]) == 0
    copied = tmp_path / '.agents' / 'skills' / DATAFLOWS_SKILL
    assert (copied / SKILL_FILE).is_file() and not copied.is_symlink()
    assert capsys.readouterr().out.startswith(f'copied {DATAFLOWS_SKILL} -> ')

    assert main(['install', '--home', '--claude', '--mode', 'link', DATAFLOWS_SKILL]) == 0
    assert (tmp_path / '.claude' / 'skills' / DATAFLOWS_SKILL).is_symlink()


def test_cli_install_all(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(['install']) == 0
    installed = sorted(path.name for path in (tmp_path / '.agents' / 'skills').iterdir())
    assert installed == skill_names()
    assert len(capsys.readouterr().out.splitlines()) == len(skill_names())


def test_cli_install_unknown(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    assert main(['install', '--dir', str(tmp_path), 'no-such-skill']) == 1
    assert 'No skill named' in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []
