#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout eef117194478115f842e08682bc769051a0a863f
bash /home/check_git_changes.sh

mkdir build

