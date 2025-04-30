#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout c25928e44fb69f5a3b1d0bbbabf75742e15269ee
bash /home/check_git_changes.sh

mkdir build

