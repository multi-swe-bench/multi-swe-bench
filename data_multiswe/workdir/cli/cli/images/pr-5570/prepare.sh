#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b352648259403c0b81dc969512354ec3cb64871e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

