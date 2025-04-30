#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 94fe6c776422a3e2a3ec00620f0d9c5ebdbee521
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

