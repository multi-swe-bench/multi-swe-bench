#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout bfc0924eacaa3c6163eb872c8948098565464192
bash /home/check_git_changes.sh
mkdir build || true

