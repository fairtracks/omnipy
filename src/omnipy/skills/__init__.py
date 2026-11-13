"""The agent skills shipped with Omnipy, and their installation for a coding agent.

A skill is a directory with a `SKILL.md` file that an agent reads when the task calls for it, in
the format of the Agent Skills specification (https://agentskills.io). Omnipy ships the skills
written for its users, one directory per skill, e.g. `omnipy-dataflows` on designing dataflows.

In the repository the skills live in `.agents/skills/`, the project directory that coding agents
read. An installed Omnipy carries a copy next to this module. `install()` makes a skill available
to the agents of another project, by default as a symlink to the copy of the installed Omnipy, so
that the skill follows Omnipy through upgrades:

    python -m omnipy.skills list
    python -m omnipy skills install
"""

from dataclasses import dataclass
from pathlib import Path
import shutil

__all__ = ['InstalledSkill', 'install', 'skill_names', 'skill_path', 'skills_dir']

SKILL_FILE = 'SKILL.md'

_INSTALLED_SKILLS_DIR = Path(__file__).parent
# src/omnipy/skills in a checkout, where the skills are in .agents/skills at the repository root
_REPO_SKILLS_DIR = Path(__file__).parents[3] / '.agents' / 'skills'


def skills_dir() -> Path:
    """The directory holding the skills: in the installed package, or in a checkout of Omnipy."""
    if any(_is_skill(path) for path in _INSTALLED_SKILLS_DIR.iterdir()):
        return _INSTALLED_SKILLS_DIR
    return _REPO_SKILLS_DIR


def skill_names() -> list[str]:
    return sorted(path.name for path in skills_dir().iterdir() if _is_skill(path))


def skill_path(name: str) -> Path:
    path = skills_dir() / name
    if not _is_skill(path):
        raise LookupError(f'No skill named {name!r}. Available skills: {", ".join(skill_names())}')
    return path


@dataclass(frozen=True)
class InstalledSkill:
    path: Path
    linked: bool


def install(name: str, target_dir: Path, copy: bool = False, force: bool = False) -> InstalledSkill:
    """Install the skill `name` as `target_dir/name`, linked to the shipped skill unless copied.

    A link keeps the skill in step with the installed Omnipy. A copy is for a skills directory
    that is not tied to one Python environment, such as one in the home directory. Where the file
    system does not support symlinks, the skill is copied instead.

    With `force`, an existing `target_dir/name` is replaced.
    """
    source = skill_path(name)
    target = target_dir / name

    if target.is_symlink() or target.exists():
        if not force:
            raise FileExistsError(f'{target} exists')
        _remove(target)
    target_dir.mkdir(parents=True, exist_ok=True)

    if not copy:
        try:
            target.symlink_to(source, target_is_directory=True)
            return InstalledSkill(target, linked=True)
        except OSError:
            pass

    shutil.copytree(source, target)
    return InstalledSkill(target, linked=False)


def _is_skill(path: Path) -> bool:
    return (path / SKILL_FILE).is_file()


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)
