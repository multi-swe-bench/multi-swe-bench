#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d86b05279f3070fcf76f7b1987cd53767346fe35
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

