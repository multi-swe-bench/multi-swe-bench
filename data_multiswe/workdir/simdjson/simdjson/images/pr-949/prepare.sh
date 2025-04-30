#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 2cc84b6e51df1b71dd08df1f2f3435df2bc47783
bash /home/check_git_changes.sh

mkdir build

