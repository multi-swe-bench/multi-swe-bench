#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout 9294e25c98f9c09a1874842dbcaae7a91336a57e
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

