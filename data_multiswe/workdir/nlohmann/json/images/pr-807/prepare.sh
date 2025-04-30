#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 8e067c0c3c8739912e24035e9656df9aa973bb9d
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

