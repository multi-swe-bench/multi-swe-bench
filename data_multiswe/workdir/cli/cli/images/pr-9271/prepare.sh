#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0f2e1ed9d19f73d20eb0dd124f4b5cba3111f2e9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

