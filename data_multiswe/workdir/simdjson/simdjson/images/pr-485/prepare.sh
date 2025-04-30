#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 76c706644a245726d263950065219c45bd156d1a
bash /home/check_git_changes.sh

mkdir build

