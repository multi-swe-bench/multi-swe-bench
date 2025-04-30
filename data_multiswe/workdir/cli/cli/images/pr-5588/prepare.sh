#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 78ae6f85c615604918ffe932dcc1883712d2061a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

