#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 23913ac371bacc6af51309d85ca4e289d88af132
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

