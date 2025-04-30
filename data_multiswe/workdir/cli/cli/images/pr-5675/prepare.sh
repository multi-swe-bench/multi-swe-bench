#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e837b7bc4d5717f7df31f2e77b813f6e260fadbb
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

