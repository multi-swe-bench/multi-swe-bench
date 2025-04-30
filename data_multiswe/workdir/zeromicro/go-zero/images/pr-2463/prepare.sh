#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout 63cfe60f1a7583865757780ebfe2a5309a542134
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

