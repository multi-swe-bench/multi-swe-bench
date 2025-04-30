#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 40b78d3847fcd2acaeca5d13912ad6ae5dd0702d
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

