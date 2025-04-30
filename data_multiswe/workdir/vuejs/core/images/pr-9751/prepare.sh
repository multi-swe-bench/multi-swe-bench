#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout c3e2c556b532656b50b8ab5cd2d9eabc26622d63
bash /home/check_git_changes.sh

pnpm install || true

