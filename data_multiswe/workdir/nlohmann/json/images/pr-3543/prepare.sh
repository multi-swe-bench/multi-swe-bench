#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout f6acdbec2c99670cf932d83cd797f08662e0b564
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

