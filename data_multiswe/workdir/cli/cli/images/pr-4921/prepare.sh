#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0d3dd7e75851342f97dd1758cabe187e946dd634
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

