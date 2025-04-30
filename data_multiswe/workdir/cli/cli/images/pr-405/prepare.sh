#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c27d7807a06a01c1248f85957cba5bf23d16aae0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

