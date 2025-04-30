#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 06f1c0d725855861535e9e65cd4d502aca7c61ed
bash /home/check_git_changes.sh
mkdir build || true

