#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout d713727f2277f2eb919a2dbbfdd534f8988aa493
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

