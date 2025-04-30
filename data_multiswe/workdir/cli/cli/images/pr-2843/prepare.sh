#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6e2c1b33b0a046a7290b645e87774752b3a0d45e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

