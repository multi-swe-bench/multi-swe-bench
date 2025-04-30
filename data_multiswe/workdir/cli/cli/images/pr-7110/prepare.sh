#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c6a693c459c22b66a2914ba2794e24d22faa8015
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

