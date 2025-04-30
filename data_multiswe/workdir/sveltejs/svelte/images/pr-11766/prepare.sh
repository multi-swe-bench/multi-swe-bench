#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout d946066c081bc1b32d8eaff8ca9fedb28b6fbc79
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

