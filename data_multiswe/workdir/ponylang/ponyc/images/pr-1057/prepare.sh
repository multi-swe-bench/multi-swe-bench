#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 0c88dd775087f862f103faacdf569e57644e4ce0
bash /home/check_git_changes.sh


    