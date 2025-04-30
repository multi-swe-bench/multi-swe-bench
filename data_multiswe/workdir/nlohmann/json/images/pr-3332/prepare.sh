#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout d8a63291cbe50411a2c513d06f3ae7c8c1a43c33
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

