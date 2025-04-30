#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 0166f455f6681144a18553d2ea0cda8946bff019
bash /home/check_git_changes.sh
mkdir build || true

