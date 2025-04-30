#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d2683a1370c5f3d97eaa1e4a4a8cfbc32c1293c2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

