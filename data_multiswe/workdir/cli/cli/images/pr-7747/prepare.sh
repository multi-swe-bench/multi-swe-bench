#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8079d18efd2e195456280d9b9742c13d33702e6a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

