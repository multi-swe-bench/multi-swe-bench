#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ad8d7bb02e36e66e28c78837f5392afd1a5187a3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

