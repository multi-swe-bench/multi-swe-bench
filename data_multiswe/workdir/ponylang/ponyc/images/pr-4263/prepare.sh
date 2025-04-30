#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9f75e9eefcc118e65439bd609218cb9aace84ae6
bash /home/check_git_changes.sh


