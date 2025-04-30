#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9e26f0ac4b65462fda4cadbb80cc2fa53e3042b3
bash /home/check_git_changes.sh


    