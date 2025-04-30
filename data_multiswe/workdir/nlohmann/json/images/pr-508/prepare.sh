#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 100bf3ef2cb6893c2384bc0114e3b6592636d2d0
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

