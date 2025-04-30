#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 541ce0e5b49269b8b39707b3d16cfbd01d79b9a0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

