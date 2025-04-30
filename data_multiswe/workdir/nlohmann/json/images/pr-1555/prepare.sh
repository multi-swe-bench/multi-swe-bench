#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout b21c04c93893bb8e277eaff9d54cfe28bc6ca131
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

