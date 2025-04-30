#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 0b345b20c888f7dc8888485768e4bf9a6be29de0
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

