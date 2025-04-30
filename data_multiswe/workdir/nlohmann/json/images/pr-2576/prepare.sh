#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f551930e5c7ef397056de121c0da82f77573cca
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

