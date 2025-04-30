#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a73880f5ddebf56c251e6394d4716e90ce7b4cdd
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

