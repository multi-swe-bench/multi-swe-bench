#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 26d33d6e387857f3d2e34f2529e7b05c7c51535f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

