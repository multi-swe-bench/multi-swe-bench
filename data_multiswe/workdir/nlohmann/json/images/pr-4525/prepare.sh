#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 1b9a9d1f2122e73b69f5d62d0ce3ebda8cd41ff0
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

