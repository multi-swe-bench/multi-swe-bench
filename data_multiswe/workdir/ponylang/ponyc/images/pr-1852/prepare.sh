#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 6631b63dd7792d84a4004bf733c1fcc92069a421
bash /home/check_git_changes.sh


    