#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 419d8bd72e02f96c3a7c1c8ac0ae5294e7f59e94
bash /home/check_git_changes.sh


    