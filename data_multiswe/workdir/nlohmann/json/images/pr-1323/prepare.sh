#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 037e93f5c09805c84460c91abee40d479d1512a6
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

