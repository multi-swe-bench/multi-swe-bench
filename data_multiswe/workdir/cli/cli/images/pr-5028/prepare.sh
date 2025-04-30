#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0a6dc76e5c3a51ec21ab7d3ec13ffc5e5cc0a4a4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

