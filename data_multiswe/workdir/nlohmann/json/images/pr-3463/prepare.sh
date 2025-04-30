#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 0c698b75ccb81c2218e0b0b3ae8e9e60ba97c6bb
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

