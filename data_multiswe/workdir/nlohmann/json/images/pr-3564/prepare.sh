#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 954b10ad3baa5d92bb9cd5bb93c7258433cd2bb2
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

