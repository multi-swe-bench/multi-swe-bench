#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout cb053bceb133e819aaaa0e68bc5864a13137cfb0
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

