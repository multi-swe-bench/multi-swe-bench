#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 40cba172ed66584cf670c98202ed474a316667e3
bash /home/check_git_changes.sh

mkdir build

