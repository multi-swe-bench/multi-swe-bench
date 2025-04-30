#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 2d48a4d9c5e8f0a5ce914922eb2a45dc0ec93ee3
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

