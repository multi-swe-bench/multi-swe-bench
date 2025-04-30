#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 88e744bafb3511aeb9530c7c5c2c114ef60769b1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

