#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 19cac63fe4b4d8fe6a4ced28de16a68659cf9035
bash /home/check_git_changes.sh
mkdir build || true

