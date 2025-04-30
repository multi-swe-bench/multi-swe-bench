#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout a58a532ecf9761eb8d91bbad3837ee62da4434b4
bash /home/check_git_changes.sh


    