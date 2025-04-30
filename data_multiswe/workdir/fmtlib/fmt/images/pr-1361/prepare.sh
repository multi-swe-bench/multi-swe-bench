#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout a5abe5d95cb8a8015913be9748a9661f3e1fbda8
bash /home/check_git_changes.sh
mkdir build || true

