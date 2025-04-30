#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 8a4bec5cf53387356738a06ba0cf4fdf086241ae
bash /home/check_git_changes.sh
mkdir build || true

