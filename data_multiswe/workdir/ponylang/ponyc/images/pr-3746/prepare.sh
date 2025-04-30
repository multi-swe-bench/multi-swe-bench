#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 151a2f50d35db7745e8a55d00e91c756b97f3dc0
bash /home/check_git_changes.sh


