#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 938f6f4bdde9c6fc7c1cea00593f8bbfc8751e0f
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

