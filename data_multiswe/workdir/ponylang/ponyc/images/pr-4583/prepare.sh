#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 115143f6bc5a90ff19c3af2bee68f3077fc5f1a3
bash /home/check_git_changes.sh


