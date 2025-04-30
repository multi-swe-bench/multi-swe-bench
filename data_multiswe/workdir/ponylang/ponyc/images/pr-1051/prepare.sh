#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 5c49115c102c7165ef825794279e80600de297a7
bash /home/check_git_changes.sh


    