#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 18e81129ee5e0e365f4ed1aaf4680423efe447dc
bash /home/check_git_changes.sh


    