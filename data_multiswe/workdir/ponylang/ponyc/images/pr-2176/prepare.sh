#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 87bca25efaa6d9329ed6c5805ac44e176068a8a4
bash /home/check_git_changes.sh


    