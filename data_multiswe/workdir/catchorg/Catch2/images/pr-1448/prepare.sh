#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 62460fafe6b54c3173bc5cbc46d05a5f071017ff
bash /home/check_git_changes.sh

mkdir build

