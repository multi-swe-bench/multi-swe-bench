#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1fe25b8376c695f7f5896323839c1055703acd7b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

