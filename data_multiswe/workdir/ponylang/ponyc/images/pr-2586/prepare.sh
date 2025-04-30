#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 3ed6c09a5f410351cb0eb9eb545eae9114cbb065
bash /home/check_git_changes.sh


    