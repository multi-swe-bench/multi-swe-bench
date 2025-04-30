#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout c7e6d8afb06cec7b8244f963dc081daf7e70f7f6
bash /home/check_git_changes.sh
mkdir build || true

