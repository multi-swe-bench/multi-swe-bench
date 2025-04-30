#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 49adbe3fe69ba20c6da25de0bf4df696ef3bb503
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

