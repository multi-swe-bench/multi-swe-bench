#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a2aa07d497de3ad53be0e3b68d1adb9923105306
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

