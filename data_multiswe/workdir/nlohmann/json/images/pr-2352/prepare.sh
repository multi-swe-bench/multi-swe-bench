#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout b888afe5f45f0ac6381aa5fa93bba7b5fc035354
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

