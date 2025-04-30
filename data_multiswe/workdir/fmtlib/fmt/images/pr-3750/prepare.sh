#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 274ba2645bdae12f6f0c7d7ca24659c4af670548
bash /home/check_git_changes.sh
mkdir build || true

