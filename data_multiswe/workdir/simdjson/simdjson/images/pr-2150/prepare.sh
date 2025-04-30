#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout e1c6a778f8800787bd6846de3f42485f39f558bb
bash /home/check_git_changes.sh

mkdir build

