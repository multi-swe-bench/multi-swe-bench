#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout d07596a0ea5e66e2677568d4c45b8d9147c9173b
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

