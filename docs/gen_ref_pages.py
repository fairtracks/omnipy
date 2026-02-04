from pathlib import Path

import mkdocs_gen_files

IGNORED_PATHS = [
    'src/omnipy/_dynamic_all.py',
]

INHERIT_MEMBERS_PATHS = [
    'src/omnipy/shared/protocols/',
    'src/omnipy/compute/',
    'src/omnipy/data/',
    'src/omnipy/engine/',
]

nav = mkdocs_gen_files.nav.Nav()


def _any_matching_paths(target_path: Path, match_path_list: list[str]) -> bool:
    return any(str(target_path).startswith(path) for path in match_path_list)


for path in sorted(Path('src').rglob('*.py')):
    print(f'Processing {path}')

    module_path = path.relative_to('src').with_suffix('')
    doc_path = path.relative_to('src').with_suffix('.md')
    full_doc_path = Path('reference', doc_path)

    parts = list(module_path.parts)

    if _any_matching_paths(path, IGNORED_PATHS) or any(
            part.startswith('_') and not part.startswith('__') for part in parts):
        print(f'Skipping {path}')
        continue

    if parts[-1] == '__init__':
        parts = parts[:-1]
        doc_path = doc_path.with_name('index.md')
        full_doc_path = full_doc_path.with_name('index.md')
    elif parts[-1] == '__main__':
        continue

    nav[tuple(parts)] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, 'w') as fd:
        identifier = '.'.join(parts)
        print('::: ' + identifier, file=fd)

        if _any_matching_paths(path, INHERIT_MEMBERS_PATHS):
            print('    options:', file=fd)
            print('      inherited_members: true', file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, Path('../') / path)

    with mkdocs_gen_files.open('reference/SUMMARY.md', 'w') as nav_file:
        nav_file.writelines(nav.build_literate_nav())
