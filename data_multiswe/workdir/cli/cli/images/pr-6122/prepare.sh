#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f488f4d5496e176300614b7bd9ded02c8572ec3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

