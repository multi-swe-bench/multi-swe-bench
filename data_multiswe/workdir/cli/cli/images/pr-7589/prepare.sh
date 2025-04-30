#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5a0f892d4aca77b55024a22ac3d353d7a3a5335d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

