#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 9b0f7066046b3bc4695ea1aff2a6ba6c31583471
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

