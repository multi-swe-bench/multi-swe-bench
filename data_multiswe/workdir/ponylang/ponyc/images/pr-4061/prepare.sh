#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 65e2cfc70fc900976ea5e93fc500f39a6844ae73
bash /home/check_git_changes.sh


