#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3dd3fb0319b0f5f406fe36a207440b32dc4cb6fd
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

