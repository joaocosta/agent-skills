#!/usr/bin/env sh
# Configure this checkout to use the repository-maintained Git hooks.
set -eu

repository_root=$(git rev-parse --show-toplevel 2>/dev/null) || {
    printf '%s\n' 'setup_git_hooks: run this command from inside the Git checkout.' >&2
    exit 1
}

cd "$repository_root"

if [ ! -f dev/hooks/pre-commit ]; then
    printf '%s\n' 'setup_git_hooks: dev/hooks/pre-commit is missing.' >&2
    exit 1
fi

git config core.hooksPath dev/hooks
printf '%s\n' 'Git hooks enabled for this checkout.'
