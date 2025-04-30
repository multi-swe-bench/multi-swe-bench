#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6e14426dfb076350796b6f081b27399a5f4be904
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

