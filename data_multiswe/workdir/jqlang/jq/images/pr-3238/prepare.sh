#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 31dac287cce2d15357c3b78a90009007e9c21493
bash /home/check_git_changes.sh
git submodule update --init

