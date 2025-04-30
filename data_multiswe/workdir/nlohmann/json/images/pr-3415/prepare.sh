#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 261cc4e509c51d53c57d0c266abd4a78f134e6a4
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

