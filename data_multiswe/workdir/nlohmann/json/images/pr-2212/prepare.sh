#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 8575fdf9ad41844692b18fb9db4d28fea4e9282a
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

