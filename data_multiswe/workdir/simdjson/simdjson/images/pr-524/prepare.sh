#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 0b21203141bd31229c77e4b1e8b22f523a4a69e0
bash /home/check_git_changes.sh

mkdir build

