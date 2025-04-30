#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2e6f2020316c744e14b0b49fdea5966f1ea7054b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

