#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 92ff87c6b77f055b0446430bf8cf65025f2c64a7
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

