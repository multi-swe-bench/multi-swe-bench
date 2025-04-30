#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 777d059b10ded7e0e4af0cfb837c9e00864b3ec2
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

