#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 74bb7b2533af3f063d0794fe3962fb5226c27751
bash /home/check_git_changes.sh

mkdir build

