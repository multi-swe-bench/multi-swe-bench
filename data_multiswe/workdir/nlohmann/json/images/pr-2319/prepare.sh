#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 1b8efed06f04a0b2ff612d55263c0496b527c00d
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

