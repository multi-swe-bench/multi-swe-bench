#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout c42bb04276af0024b49aa46918eec69ad56570a5
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

