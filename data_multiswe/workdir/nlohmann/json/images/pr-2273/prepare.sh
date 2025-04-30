#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a521cbd3657eea6ba90cded2aecca93e3cd78d4
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

