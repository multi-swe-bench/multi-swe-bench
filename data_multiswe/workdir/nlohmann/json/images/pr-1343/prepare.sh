#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout d2e6e1bf5852d9c8f2470c7c99eb6e600bb79138
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

