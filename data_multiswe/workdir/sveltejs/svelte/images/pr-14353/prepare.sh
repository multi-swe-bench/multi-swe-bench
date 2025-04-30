#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout b145035a00525770abe9116e3887c050e19340ea
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

