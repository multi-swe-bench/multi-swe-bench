#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fab84beb900c1789076cd7b538bb05739d41cea6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

