#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout ca368192917b76bb43e0892d4f14cbdf18e1f7d6
bash /home/check_git_changes.sh


