#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9a12f91bec2d57a23a576d30ad879843657ca020
bash /home/check_git_changes.sh


    