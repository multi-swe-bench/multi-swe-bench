#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout ede66678580596028bcd6e18871a35a54bac01d7
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

