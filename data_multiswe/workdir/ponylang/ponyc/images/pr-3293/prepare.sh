#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout bcfc15fdc61ddd5925a7e3ddc28f3fc1fc3679d4
bash /home/check_git_changes.sh


    