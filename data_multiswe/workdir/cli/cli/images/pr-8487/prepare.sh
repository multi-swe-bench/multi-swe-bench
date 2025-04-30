#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 29bd9dc6ebbf220f3861204fb9b288a9e13db0de
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

