#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 661d962112d0e8f395cedf053ce25947b809348b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

