#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout d794a929da09741f593572c11822b21289cc2f74
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

