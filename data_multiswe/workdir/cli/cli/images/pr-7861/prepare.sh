#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c5f88bb551e22b04a3799561f3abea4892012eff
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

