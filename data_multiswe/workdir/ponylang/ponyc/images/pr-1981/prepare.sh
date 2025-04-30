#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 560c412e0eb23a0b922a9ba3bea064c14f18d84a
bash /home/check_git_changes.sh


    