#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f1ea794bf1d598f5b9b99ceb92a199d20f9ae251
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

