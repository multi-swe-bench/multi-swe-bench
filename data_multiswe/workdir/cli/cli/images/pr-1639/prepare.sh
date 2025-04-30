#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b2f3c326e28c10677fded95c4b7f454d86273e21
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

