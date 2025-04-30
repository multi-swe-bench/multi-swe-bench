#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 682b45d3abd7b24381bfc56423da85c3527785c7
bash /home/check_git_changes.sh


    