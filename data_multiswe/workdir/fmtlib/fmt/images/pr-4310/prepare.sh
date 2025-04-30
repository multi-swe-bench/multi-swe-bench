#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 01914f0389ef6ff151c289670f6910e059d5063f
bash /home/check_git_changes.sh
mkdir build || true

