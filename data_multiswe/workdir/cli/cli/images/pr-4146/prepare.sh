#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 05328fbe13491b08d31f47e080073bfc6abf1400
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

