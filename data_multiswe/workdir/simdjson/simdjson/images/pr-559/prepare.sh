#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 032936a7b54f3c705af3b60b798045c940a2eb86
bash /home/check_git_changes.sh

mkdir build

