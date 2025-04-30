#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6a48a604f095f0ca2c1d78629bf5c0b55774f2b5
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

