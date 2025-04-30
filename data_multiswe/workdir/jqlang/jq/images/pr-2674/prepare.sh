#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout cac3ea37262c3fdf77d6947b136873b12d3794ea
bash /home/check_git_changes.sh
git submodule update --init

