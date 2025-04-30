#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout e5e388df132fdff91d4e6afb8d8e66be175fa051
bash /home/check_git_changes.sh


    