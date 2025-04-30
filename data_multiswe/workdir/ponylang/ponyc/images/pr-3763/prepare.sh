#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 847c83430e8dfa645ba753a84754004134a9ca60
bash /home/check_git_changes.sh


