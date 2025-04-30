#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 87800419f561aad044b0a46bbd4897fb5d54f620
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

