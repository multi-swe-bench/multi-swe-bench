#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ede1705bf24c55e2d37364fe24d225f8f505f8ee
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

