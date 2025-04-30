#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f3d2a3be7be0235006f9a66b4fb62316d62c31e
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

