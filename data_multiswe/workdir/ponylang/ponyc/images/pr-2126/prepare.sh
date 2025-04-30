#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8badbf6b6e6c0da9c99eaac59c90d98e1b3b8dad
bash /home/check_git_changes.sh


    