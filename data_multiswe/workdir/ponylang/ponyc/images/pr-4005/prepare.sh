#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 91c59d376f8515153c67a9460dec6f701ca129df
bash /home/check_git_changes.sh


