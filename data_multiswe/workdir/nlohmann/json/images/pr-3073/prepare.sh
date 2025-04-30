#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b1cb9eee129632abc4fa684688691568e26c9e9
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

