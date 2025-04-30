#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout e86d34aef1fd6abff7d8e777817f09be36509668
bash /home/check_git_changes.sh


