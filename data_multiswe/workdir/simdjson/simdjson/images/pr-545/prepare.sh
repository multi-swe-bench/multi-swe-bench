#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout e4e89fe27a37a1abf70387d07adfb3b1b9f115ef
bash /home/check_git_changes.sh

mkdir build

