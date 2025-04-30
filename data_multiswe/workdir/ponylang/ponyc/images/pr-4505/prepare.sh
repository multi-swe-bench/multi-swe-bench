#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout be1000c459a714e164c52b677c492fc9af385ffe
bash /home/check_git_changes.sh


