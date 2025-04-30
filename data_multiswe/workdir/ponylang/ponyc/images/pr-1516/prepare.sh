#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout c6cd013119eb1f1a3b9b76a8111ac1877f61f9d8
bash /home/check_git_changes.sh


    