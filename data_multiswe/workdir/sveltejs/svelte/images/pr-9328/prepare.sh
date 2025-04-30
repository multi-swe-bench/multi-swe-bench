#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f508a011bc8051ab9f82cafa97c5292a4453b92
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

