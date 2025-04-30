#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a358bb73db9bb3c28f72d0f7ec81c8195829c3fb
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

