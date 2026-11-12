#!/bin/sh
set -eu

if [ "${OMNIPY_README_CHECK_NAMES_ONLY:-}" = 1 ]; then
    exec uv run --offline python docs/gen_readme.py --check
fi

untracked_images() {
    git ls-files --others -- 'docs/images/readme/*.svg'
}

if [ -n "$(untracked_images)" ]; then
    echo 'Untracked README images exist. Stage or move them before generating the README.' >&2
    untracked_images >&2
    exit 1
fi

uv run --offline python docs/gen_readme.py

if [ -n "$(untracked_images)" ]; then
    echo 'New README images were generated. Review and stage them.' >&2
    untracked_images >&2
    exit 1
fi
