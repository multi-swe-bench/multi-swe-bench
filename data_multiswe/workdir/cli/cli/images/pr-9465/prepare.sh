#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c81ccab4b8bb1ef1c774f4ba9851e9dcb11fa5e7
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

