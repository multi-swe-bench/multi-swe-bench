#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e2e818204e346b0c8e5afa1be5ad06159d42d15
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

