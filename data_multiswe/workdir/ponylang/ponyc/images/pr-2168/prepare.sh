#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout ae5fabe6fdf7c99f3e797b85674ded5d52cde7a2
bash /home/check_git_changes.sh


    