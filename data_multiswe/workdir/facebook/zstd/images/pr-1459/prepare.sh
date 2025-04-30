#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout d0e15f8d327f72f891d4cae80850e3303f31ddb5
bash /home/check_git_changes.sh

