#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9c04a3730066df1372293efe44556460fecd57c4
bash /home/check_git_changes.sh


    