#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 46474010307f209ddfb1454844f8b4432ffe6f11
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

