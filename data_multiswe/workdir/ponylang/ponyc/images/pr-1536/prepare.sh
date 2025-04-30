#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 9739cad84706037682dade0ee7a10d4641b099ce
bash /home/check_git_changes.sh


    