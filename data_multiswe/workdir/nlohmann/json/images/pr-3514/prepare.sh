#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 6b97599a274b9b72caffa1332d5384c9aac27590
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

