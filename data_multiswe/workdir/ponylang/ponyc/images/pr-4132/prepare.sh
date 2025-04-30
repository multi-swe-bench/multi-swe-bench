#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 7b07d4d3545632369b4ea5106770cbb57b74a6dc
bash /home/check_git_changes.sh


