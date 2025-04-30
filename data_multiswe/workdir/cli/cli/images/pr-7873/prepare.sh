#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 330ad32c316e727fa46c7c425b0523ea24525de5
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

