#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 7cbcee3d831241a8bd3588ae92d3f27e3641e25f
bash /home/check_git_changes.sh

pnpm install || true

