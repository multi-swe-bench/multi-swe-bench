#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 7b6cf5918bc9a4b85d1e3fb9ff65348d6dce5d10
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

