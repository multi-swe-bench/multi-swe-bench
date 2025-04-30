#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 6cd04aa858f2d92105c0fbd65cdafb96428db002
bash /home/check_git_changes.sh

mkdir build

