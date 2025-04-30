#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout dd672939a0dcbe50afafb91c430a882aff4bcf20
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

