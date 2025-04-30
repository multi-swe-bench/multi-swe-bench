#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout e45eaf6e3085fd5e51907cff1b93d747620ffc00
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

