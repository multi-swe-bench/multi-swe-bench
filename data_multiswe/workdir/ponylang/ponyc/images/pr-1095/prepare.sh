#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout cdd5165d27e62b4b36541edf7ba83d6347ce3aa3
bash /home/check_git_changes.sh


    