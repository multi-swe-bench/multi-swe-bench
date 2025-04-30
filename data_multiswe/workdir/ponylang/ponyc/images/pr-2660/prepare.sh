#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 02f6db76b30bc839e1a2c2d7a329127f15972039
bash /home/check_git_changes.sh


    