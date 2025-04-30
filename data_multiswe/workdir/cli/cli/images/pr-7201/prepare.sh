#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0b9b1f710f73c9df3350c64e2bdb598985d88743
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

