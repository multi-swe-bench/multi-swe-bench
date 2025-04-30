#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 14d339d9ba87e87f34b7a25f00200a2062f87039
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

