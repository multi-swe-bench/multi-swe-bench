#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b9553fdd653270530efca555ab6383a085368e26
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

