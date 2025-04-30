#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 0dd91e20d5e8c7c41154acbb4fbe6b9d37688ea3
bash /home/check_git_changes.sh
mkdir build || true

