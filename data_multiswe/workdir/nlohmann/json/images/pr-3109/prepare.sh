#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 7440786b813534b567f6f6b87afb2aa19f97cc89
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

