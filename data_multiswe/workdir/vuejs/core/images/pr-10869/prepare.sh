#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a8d54850610b65091b52c825b66e3510f4b9fe8
bash /home/check_git_changes.sh

pnpm install || true

