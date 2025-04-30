#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ccccac394b97df54ee33ea1679ea7126884aeeba
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

