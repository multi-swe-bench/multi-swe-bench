#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ebcf3a10225a9b7c9422f6b63ff798d695f7f0a2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

