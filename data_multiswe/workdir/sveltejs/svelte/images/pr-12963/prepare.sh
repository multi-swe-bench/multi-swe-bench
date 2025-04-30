#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 803ebd56767eec5daf560f52bb88e6ab4ff97367
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

