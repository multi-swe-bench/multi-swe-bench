#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 438de04fb2a753287bfd9fd420711cc7cd971012
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

