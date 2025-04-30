#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout eab690d31a7203ac23334460c9ae68844d43dc26
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

