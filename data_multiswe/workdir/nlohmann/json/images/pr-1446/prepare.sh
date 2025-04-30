#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout dffae1082f01c083bc762ff21f57d7a8546f8c82
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

