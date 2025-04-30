#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9668981264707da16f62625b15488d8b39e6e499
bash /home/check_git_changes.sh


