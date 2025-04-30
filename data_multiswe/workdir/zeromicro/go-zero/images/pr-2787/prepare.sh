#!/bin/bash
set -e

cd /home/go-zero
git reset --hard
bash /home/check_git_changes.sh
git checkout b2571883cae4290b4ef0dd0a583d22c14116c4a3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

