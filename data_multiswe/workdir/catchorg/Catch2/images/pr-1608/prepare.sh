#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 979bbf03bb00bc55ca09783791b5091a2247df68
bash /home/check_git_changes.sh

mkdir build

