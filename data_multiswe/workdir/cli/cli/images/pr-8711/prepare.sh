#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b07f955c23fb54c400b169d39255569e240b324e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

