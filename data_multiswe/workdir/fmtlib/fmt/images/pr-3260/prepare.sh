#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 2622cd23e69b67316cf678a97c268a874774c0e1
bash /home/check_git_changes.sh
mkdir build || true

