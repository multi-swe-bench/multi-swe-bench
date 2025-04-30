#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 727b72666713909d318f24f03065ce2e488566d5
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

