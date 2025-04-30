#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8823316c0666ae776a4aa523ad094e2d8ee10b90
bash /home/check_git_changes.sh


    