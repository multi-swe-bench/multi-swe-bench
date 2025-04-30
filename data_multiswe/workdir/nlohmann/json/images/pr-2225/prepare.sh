#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 5ba0f65c34832aa18fb2b582d58a0c1f92c93bfb
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

