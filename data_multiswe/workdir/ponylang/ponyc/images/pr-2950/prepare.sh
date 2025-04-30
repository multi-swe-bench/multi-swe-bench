#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 5fc1b04ca78b050cdf6d5f7a630d878a705a5710
bash /home/check_git_changes.sh


    