#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 7f7504b3f532c6cd7d6de405241f774df6b4b666
bash /home/check_git_changes.sh
mkdir build || true

