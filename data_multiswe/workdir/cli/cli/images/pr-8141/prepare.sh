#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3443a752a9949ee4f954a84f7ab94a4b99df1b27
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

