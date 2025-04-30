#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 3790bd9ae059a8c3700ff90895c487dba19b6092
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

