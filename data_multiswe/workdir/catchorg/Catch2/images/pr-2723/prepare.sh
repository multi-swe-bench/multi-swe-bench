#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 4acc51828f7f93f3b2058a63f54d112af4034503
bash /home/check_git_changes.sh

mkdir build

