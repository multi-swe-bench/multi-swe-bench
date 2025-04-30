#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1c260191ee39659ebb7f05e18781bc54b5b7fac9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

