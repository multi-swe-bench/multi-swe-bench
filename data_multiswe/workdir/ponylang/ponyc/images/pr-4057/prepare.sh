#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout bc0d988f909d6bb2698b836bb5f592aa567f6fb6
bash /home/check_git_changes.sh


