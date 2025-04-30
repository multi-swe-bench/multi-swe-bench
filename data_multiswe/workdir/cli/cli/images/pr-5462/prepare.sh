#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout eb08a9bd29ef9e8b07815a38a168069caf66f240
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

