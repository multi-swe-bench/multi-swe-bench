#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout ee32bfc1c263900d5c31cf8a8c5429048719e42a
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

