#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 4b4fefa254346524c787b862e35e4fbb70e01e95
bash /home/check_git_changes.sh
git submodule update --init

