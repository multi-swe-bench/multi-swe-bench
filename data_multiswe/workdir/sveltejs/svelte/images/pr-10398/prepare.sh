#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d23805a6f047c6e99b9bc6fbb5b6c6673093afe4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

