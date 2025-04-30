#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 86f326531c2abc4a976db4c27656c7b530363fdf
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

