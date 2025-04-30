#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout ac20e0541167fa6893f2fbcf43aa68b784b3bd8b
bash /home/check_git_changes.sh


    