#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 4860cccd72b93ba15dcfbbefa5f1e1b46532f6c6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

