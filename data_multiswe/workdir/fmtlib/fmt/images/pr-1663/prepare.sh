#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 8d9d528bf52c60864802844e8acf16db09dae19a
bash /home/check_git_changes.sh
mkdir build || true

