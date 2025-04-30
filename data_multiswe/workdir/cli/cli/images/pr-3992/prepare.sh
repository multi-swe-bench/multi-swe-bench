#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 161de77fd707a0b0314e96ac6687319bd001b7af
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

