#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout e21488fc4b4e188711ff6b106b5d350d68249ba4
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

