#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout e830bc502fe38852654a1f03f963001fecb54a86
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

