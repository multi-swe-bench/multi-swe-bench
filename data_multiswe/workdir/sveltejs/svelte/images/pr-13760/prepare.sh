#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout ef205d960e1ad723a883afc0df75a57454f151fc
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

