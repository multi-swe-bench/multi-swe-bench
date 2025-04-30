#!/bin/bash
set -e

cd /home/insomnia
git reset --hard
bash /home/check_git_changes.sh
git checkout 44642a49e9a104a53964b3b2b9c589910d391236
bash /home/check_git_changes.sh

npm ci 

