#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout cbafed349493dd8b072b5c1c5ac7f7c0ef0ed7df
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

