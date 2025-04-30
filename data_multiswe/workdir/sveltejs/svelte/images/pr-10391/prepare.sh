#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b6fcc149b87720a431eb636ce291a0c0125b0bae
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

