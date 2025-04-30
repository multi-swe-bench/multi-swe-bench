#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4d20aa78733aa1e6f8c8d35dd27e9b4979ae4e6f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

