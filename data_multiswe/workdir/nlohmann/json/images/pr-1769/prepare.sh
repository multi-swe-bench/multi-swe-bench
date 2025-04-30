#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 99d7518d21cbbfe91d341a5431438bf7559c6974
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

