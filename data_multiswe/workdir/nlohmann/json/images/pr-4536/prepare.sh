#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout e6cafa573aac6ed9227f752a5371c0b3f436307d
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

