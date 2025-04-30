#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 67bf7a80673ce9e1a6f5f5e7ab70be2b89a05690
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

