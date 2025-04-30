#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a22b7ca41cdf736eb75268464e1b72c3890fd469
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

