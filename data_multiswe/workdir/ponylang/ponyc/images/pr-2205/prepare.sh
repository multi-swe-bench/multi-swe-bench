#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 25fa3b158281bee9fd0778de618ad8968d5ed026
bash /home/check_git_changes.sh


    