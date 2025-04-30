#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 09b09810dd812e3ede54b59ad9d6912b946ac6c5
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

