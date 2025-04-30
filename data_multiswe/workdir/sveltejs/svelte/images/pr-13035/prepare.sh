#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e03dae95da33b0149c24772290f301d72b519853
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

