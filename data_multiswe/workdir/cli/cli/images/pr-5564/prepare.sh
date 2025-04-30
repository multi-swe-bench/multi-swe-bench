#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b57746a878f9bd3dc443149429179e580b83d4a0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

