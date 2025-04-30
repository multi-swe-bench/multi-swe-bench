#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 8e04a91c6701aef2b41bf99c157107458f82ef23
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

