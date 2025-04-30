#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 13342cb272d51efb4a8f9b57b9d79aaaf757ec70
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

