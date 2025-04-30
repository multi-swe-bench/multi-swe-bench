#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7d0a7f98e1dd6a762ac1b82c8c924c943f254621
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

