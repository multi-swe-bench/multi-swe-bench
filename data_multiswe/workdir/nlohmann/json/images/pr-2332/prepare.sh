#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 1da931730a73365a5a817c8571d36c9ef024dd57
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

