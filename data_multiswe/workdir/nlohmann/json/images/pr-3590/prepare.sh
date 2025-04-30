#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout d1d79b930d7c10b76f03db0c30392527e5230995
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

