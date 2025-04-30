#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 9426074ce85da2121c315cae8574d8eaca520cb7
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

