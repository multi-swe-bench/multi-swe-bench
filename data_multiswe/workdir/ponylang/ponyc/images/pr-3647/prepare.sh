#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9d976fea89155a27732f04088556834811eeed72
bash /home/check_git_changes.sh


