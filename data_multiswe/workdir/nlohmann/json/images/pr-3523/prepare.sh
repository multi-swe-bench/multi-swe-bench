#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout b6d00d18974358ab1d55dcc3379d0ee3052deb4e
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

