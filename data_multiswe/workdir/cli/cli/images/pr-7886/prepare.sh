#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6fc6b87484a813275ad54d576a73e7926fc70033
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

