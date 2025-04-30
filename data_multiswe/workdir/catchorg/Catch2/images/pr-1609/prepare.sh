#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout bd703dd74be7fd2413eb0c01662a491bcebea430
bash /home/check_git_changes.sh

mkdir build

