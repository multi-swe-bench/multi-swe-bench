#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout bbdb29c6583e9e68f7f2bdce59a7384f061e0e32
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

