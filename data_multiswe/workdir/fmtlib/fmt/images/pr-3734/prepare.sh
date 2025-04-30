#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout f5750892436a667fe622e5ecc8a02c15a5d9bc88
bash /home/check_git_changes.sh
mkdir build || true

