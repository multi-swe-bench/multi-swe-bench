#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout c0c9432b64091fa15fd8619cfb06828735356a42
bash /home/check_git_changes.sh

pnpm install || true

