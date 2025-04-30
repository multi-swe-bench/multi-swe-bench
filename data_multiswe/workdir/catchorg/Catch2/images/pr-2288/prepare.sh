#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 85c9544fa4c9625b9656d9bd765e54f8e639287f
bash /home/check_git_changes.sh

mkdir build

