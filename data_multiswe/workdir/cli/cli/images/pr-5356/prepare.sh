#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3a949203c4b6ec1b3295edbe1d2e88cbe94960cf
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

