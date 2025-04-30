#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 661b23edeb52d400cf5812e7330f14f05c072fab
bash /home/check_git_changes.sh
mkdir build || true

