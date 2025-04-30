#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout b02e3bb0b6397b5e5f2c92b163c8fa25c414c635
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

