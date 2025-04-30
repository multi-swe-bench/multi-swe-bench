#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout dd0583dda3b7e6568ce592033dd63e0b364fecab
bash /home/check_git_changes.sh


