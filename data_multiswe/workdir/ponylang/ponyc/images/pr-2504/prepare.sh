#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8b6bb05e2840edc16a14a52509842730109b0d6f
bash /home/check_git_changes.sh


    