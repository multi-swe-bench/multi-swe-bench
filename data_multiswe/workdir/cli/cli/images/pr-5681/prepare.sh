#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1e8cb9c1b2ec0ee6c2ba0f970286a8c7c3431328
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

