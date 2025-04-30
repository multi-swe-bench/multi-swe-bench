#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout e839f58a2ac1bfe966ebf17a1971167e17b6921d
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

