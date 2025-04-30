#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout eaa8efb950be5d8f1803a99b06f76cf398c67cb8
bash /home/check_git_changes.sh
mkdir build || true

