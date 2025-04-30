#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 8910b3cd9fc71a30a340c8159a83991be7aee5be
bash /home/check_git_changes.sh


    