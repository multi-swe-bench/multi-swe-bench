#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b20dfc03218d1e6d6036689f9f79a8a6c254344
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

