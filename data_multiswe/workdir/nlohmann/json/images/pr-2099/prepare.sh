#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 1de30bc6111a6c063c4aa2e3eccefce8c09e1c62
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

