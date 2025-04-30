#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3cc4c40dcb3c3fcc5f0f8e89fed9a7db307b3561
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

