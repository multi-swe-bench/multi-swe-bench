#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 9958dde3daac1c2803fa72eb4ca98fab6798a932
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

