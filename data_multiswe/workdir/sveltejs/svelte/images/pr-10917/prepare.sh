#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 7e584e40d75a4afa93c6433f0efdfcc31424eb1a
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

